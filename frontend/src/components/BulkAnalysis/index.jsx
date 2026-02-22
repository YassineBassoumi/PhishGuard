import React, { useState } from 'react';
import './BulkAnalysis.css';
import { useAuth } from '../../contexts/AuthContext';
import BulkAnalysisForm from './BulkAnalysisForm';
import BulkAnalysisResults from './BulkAnalysisResults';

const BulkAnalysis = ({ initialEmails = null }) => {
    const { token } = useAuth();
    const [emails, setEmails] = useState(['', '', '']);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState(null);
    const [progress, setProgress] = useState(0);

    // Load initial emails if provided (from Gmail multi-select)
    React.useEffect(() => {
        if (initialEmails && initialEmails.length > 0) {
            setEmails(initialEmails);
        }
    }, [initialEmails]);

    const handleEmailChange = (index, value) => {
        const newEmails = [...emails];
        newEmails[index] = value;
        setEmails(newEmails);
    };

    const addEmailField = () => {
        if (emails.length < 50) {
            setEmails([...emails, '']);
        }
    };

    const removeEmailField = (index) => {
        if (emails.length > 1) {
            const newEmails = emails.filter((_, i) => i !== index);
            setEmails(newEmails);
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const pastedText = e.clipboardData.getData('text');
        const lines = pastedText.split('\n\n').filter(line => line.trim());
        
        if (lines.length > 1) {
            // Multiple emails pasted
            const newEmails = lines.slice(0, 50); // Max 50
            setEmails(newEmails);
        } else {
            // Single email, paste normally
            const index = parseInt(e.target.dataset.index);
            handleEmailChange(index, pastedText);
        }
    };

    const handleAnalyze = async () => {
        // Filter out empty emails
        const validEmails = emails.filter(email => email.trim());
        
        if (validEmails.length === 0) {
            alert('Veuillez entrer au moins un email à analyser');
            return;
        }

        setIsAnalyzing(true);
        setProgress(0);
        setResults(null);

        try {
            // Simulate progress (since we don't have real-time updates)
            const progressInterval = setInterval(() => {
                setProgress(prev => Math.min(prev + 10, 90));
            }, 200);

            const response = await fetch('http://localhost:8000/api/analyze-bulk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ emails: validEmails })
            });

            clearInterval(progressInterval);
            setProgress(100);

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error('Bulk analysis failed:', error);
            alert('Erreur lors de l\'analyse: ' + error.message);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleClear = () => {
        setEmails(['', '', '']);
        setResults(null);
        setProgress(0);
    };

    const getThreatColor = (threatLevel) => {
        switch (threatLevel) {
            case 'safe': return '#10b981';
            case 'suspicious': return '#f59e0b';
            case 'dangerous': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const getThreatIcon = (threatLevel) => {
        switch (threatLevel) {
            case 'safe': return '✓';
            case 'suspicious': return '⚠';
            case 'dangerous': return '✕';
            default: return '?';
        }
    };

    return (
        <div className="bulk-analysis-container fade-in-up">
            {!results ? (
                <BulkAnalysisForm
                    emails={emails}
                    onEmailChange={handleEmailChange}
                    onPaste={handlePaste}
                    onAddEmail={addEmailField}
                    onRemoveEmail={removeEmailField}
                    onAnalyze={handleAnalyze}
                    onClear={handleClear}
                    isAnalyzing={isAnalyzing}
                    progress={progress}
                    initialEmails={initialEmails}
                />
            ) : (
                <BulkAnalysisResults
                    results={results}
                    onNewAnalysis={handleClear}
                    getThreatColor={getThreatColor}
                    getThreatIcon={getThreatIcon}
                />
            )}
        </div>
    );
};

export default BulkAnalysis;
