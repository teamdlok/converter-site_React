import React, { useState } from 'react';
import axios from 'axios';

const FileUploadComponent = () => {
    const [file, setFile] = useState(null);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setUploadedFile(null); // Сбрасываем предыдущий файл при выборе нового
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file first');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            setUploadStatus('Uploading...');
            const response = await axios.post('http://localhost:8000/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            
            setUploadStatus('Upload successful!');
            setError('');
            setUploadedFile(response.data); // Сохраняем информацию о загруженном файле
            console.log('File uploaded:', response.data);
        } catch (err) {
            setError('Error uploading file');
            setUploadStatus('');
            console.error('Upload error:', err);
        }
    };

    // Функция для определения типа контента
    const renderFilePreview = () => {
        if (!uploadedFile) return null;

        const fileUrl = uploadedFile.file;
        const fileType = file.type.split('/')[0]; // Получаем общий тип (image, video и т.д.)
        const fileName = file.name.toLowerCase();

        return (
            <div className="file-preview">
                <h3>Uploaded File:</h3>
                {fileType === 'image' && (
                    <img 
                        src={`http://127.0.0.1:8000${fileUrl}`} 
                        alt="Uploaded content" 
                        style={{ maxWidth: '100%', maxHeight: '400px' }}
                    />
                )}
                
                {fileType === 'video' && (
                    <video controls style={{ maxWidth: '100%' }}>
                        <source src={fileUrl} type={file.type} />
                        Your browser does not support the video tag.
                    </video>
                )}

                {(fileType !== 'image' && fileType !== 'video') && (
                    <div>
                        <p>File type: {file.type}</p>
                        <a 
                            href={fileUrl} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            download
                        >
                            Download File
                        </a>
                    </div>
                )}

                <div className="file-info">
                    <p>File name: {uploadedFile.file.split('/').pop()}</p>
                    <p>File size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p>Uploaded at: {new Date(uploadedFile.uploaded_at).toLocaleString()}</p>
                </div>
            </div>
        );
    };

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
            <h2>File Upload</h2>
            <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
                <input 
                    type="file" 
                    onChange={handleFileChange} 
                    style={{ margin: '10px 0' }}
                />
                <button 
                    type="submit" 
                    style={{
                        padding: '10px 20px',
                        background: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Upload
                </button>
            </form>

            {uploadStatus && (
                <p style={{ color: '#4CAF50' }}>{uploadStatus}</p>
            )}

            {error && (
                <p style={{ color: 'red' }}>{error}</p>
            )}

            {file && !uploadedFile && (
                <div style={{ margin: '20px 0' }}>
                    <p>Selected File: {file.name}</p>
                    <p>File Size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p>File Type: {file.type}</p>
                </div>
            )}

            {uploadedFile && renderFilePreview()}
        </div>
    );
};

export default FileUploadComponent;