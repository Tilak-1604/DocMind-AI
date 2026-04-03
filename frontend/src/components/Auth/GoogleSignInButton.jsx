import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

const GoogleSignInButton = ({ onGoogleResponse, loading = false }) => {
    const googleBtnRef = useRef(null);

    useEffect(() => {
        const initializeGoogle = () => {
            /* global google */
            if (window.google && !loading) {
                google.accounts.id.initialize({
                    client_id: "953881870828-va0i3pq91el796ragitm2pj70nmuo6mo.apps.googleusercontent.com",
                    callback: onGoogleResponse
                });

                if (googleBtnRef.current) {
                    google.accounts.id.renderButton(
                        googleBtnRef.current,
                        { 
                            theme: "outline", 
                            size: "large", 
                            width: "350",
                            shape: "pill",
                            logo_alignment: "center"
                        }
                    );
                }
            }
        };

        // Retry mechanism in case SDK loads late
        const timer = setTimeout(initializeGoogle, 100);
        return () => clearTimeout(timer);
    }, [onGoogleResponse, loading]);

    return (
        <div className="flex flex-col items-center justify-center w-full min-h-[50px]">
            {loading ? (
                <motion.div 
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="flex items-center gap-3 px-8 py-3 bg-white text-black rounded-full shadow-lg"
                >
                    <div className="w-4 h-4 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                    <span className="text-sm font-medium">Securing session...</span>
                </motion.div>
            ) : (
                <motion.div 
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    ref={googleBtnRef} 
                    className="w-full flex justify-center overflow-hidden rounded-full shadow-md"
                />
            )}
        </div>
    );
};

export default GoogleSignInButton;
