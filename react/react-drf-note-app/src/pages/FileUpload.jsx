import React, { useState } from 'react';
import axios from 'axios';
import "./FileUpload.css"

const FileUploadComponent = () => {
    const [file, setFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [error, setError] = useState('');
    const [uploadedFileUrl, setUploadedFileUrl] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const uploadToMinio = async (presignedUrl, file) => {
        try {
            const response = await axios.put(presignedUrl, file, {
                headers: {
                    'Content-Type': file.type,
                    'x-amz-acl': 'public-read',
                    "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
                    "x-amz-disable-multipart": "true" //Отключили multipart чтобы объекты нормаль отображались в файловой системе
                }
            });
            return response.status === 200;
        } catch (err) {
            console.error('Minio upload error:', err);
            return false;
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file first');
            return;
        }

        try {
            setUploadStatus('Generating presigned URL...');
            
            // Step 1: Get presigned URL from DRF
            const presignedResponse = await axios.post(
                'http://127.0.0.1:8000/api/generate-presigned-url/',
                {
                    file_name: file.name,
                    content_type: file.type
                }
            );

            // Step 2: Upload directly to Minio
            setUploadStatus('Uploading to Minio...');
            const uploadSuccess = await uploadToMinio(
                presignedResponse.data.presigned_url,
                file
            );

            if (uploadSuccess) {
                console.log(presignedResponse.data)
                setUploadStatus('Upload successful!');
                setUploadedFileUrl(presignedResponse.data.file_url);
                setError('');
            } else {
                throw new Error('Failed to upload to Minio');
            }
        } catch (err) {
            setError('Error uploading file');
            setUploadStatus('');
            console.error('Upload error:', err);
        }
    };

    const renderPreview = () => {
        if (!uploadedFileUrl) return null;

        const fileType = file.type.split('/')[0];
        
        return (
            <div className="preview">
                <h3>Uploaded File:</h3>
                {fileType === 'image' && (
                    <img src={`http://${uploadedFileUrl}`} style={{ maxWidth: '100%' }} />
                )}
                {fileType === 'video' && (
                    <video controls style={{ maxWidth: '100%' }}>
                        <source src={uploadedFileUrl} type={file.type} />
                    </video>
                )}
                {fileType !== 'image' && fileType !== 'video' && (
                    <a href={uploadedFileUrl} target="_blank" rel="no open">
                        View File
                    </a>
                )}
            </div>
        );
    };

    return (
        <div>
            <h2 className='headertext'>Upload File to Minio</h2>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} />
                <button type="submit">Upload</button>
            </form>
            
            {uploadStatus && <p>{uploadStatus}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {renderPreview()}
        </div>
    );
};

export default FileUploadComponent;