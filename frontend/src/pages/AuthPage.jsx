import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { ShieldCheck, MoveRight, Mail, Lock, User, LogIn, UserPlus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/UI/Logo';
import GoogleSignInButton from '../components/Auth/GoogleSignInButton';

const AuthPage = () => {
    const { googleLogin, login, register, status } = useAuth();
    const navigate = useNavigate();
    
    // Local State for Manual Auth
    const [isLoginMode, setIsLoginMode] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (status === 'authenticated') {
            navigate('/dashboard');
        }
    }, [status, navigate]);

    // Handle Manual Sign In / Sign Up
    const handleManualAuth = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        const loadingToast = toast.loading(isLoginMode ? 'Signing in...' : 'Creating account...');
        
        try {
            if (isLoginMode) {
                const user = await login(email, password);
                toast.success(`Welcome back, ${user.name}!`, { id: loadingToast, icon: '🚀' });
            } else {
                const user = await register(email, password, name);
                toast.success('Account created successfully!', { id: loadingToast, icon: '🎉' });
            }
        } catch (err) {
            console.error('Manual Auth Failed', err);
            toast.error(
                err.response?.data?.message || err.response?.data || 'Authentication failed. Please check your credentials.', 
                { id: loadingToast }
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleGoogleResponse = async (response) => {
        try {
            const result = await googleLogin(response.credential);
            toast.success(`Welcome back, ${result.name}!`, {
                icon: '🚀',
                style: {
                    borderRadius: '12px',
                    background: '#1a1a2e',
                    color: '#fff',
                    border: '1px solid rgba(99, 102, 241, 0.2)'
                },
            });
        } catch (err) {
            console.error('Google Auth Failed', err);
            toast.error('Authentication failed. Please try again.', {
                style: {
                    borderRadius: '12px',
                    background: '#3e1a1a',
                    color: '#ffbaba',
                    border: '1px solid rgba(255, 99, 71, 0.2)'
                },
            });
        }
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Decorations */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 blur-[120px] rounded-full pointer-events-none" />

            <motion.div 
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                    duration: 0.8, 
                    ease: [0.16, 1, 0.3, 1], // Custom professional ease
                    delay: 0.2 
                }}
                className="glass w-full max-w-[400px] p-8 md:p-10 flex flex-col items-center shadow-2xl relative z-10 mx-auto"
            >
                {/* Logo & Brand */}
                <motion.div 
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="mb-6"
                >
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                        <div className="relative p-2.5 bg-black rounded-full border border-white/5">
                            <Logo className="w-10 h-10" />
                        </div>
                    </div>
                </motion.div>

                <div className="text-center mb-8">
                    <motion.h1 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60 mb-2"
                    >
                        {isLoginMode ? 'Welcome back' : 'Create an account'}
                    </motion.h1>
                    <motion.p 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.7 }}
                        className="text-gray-400 text-sm leading-relaxed"
                    >
                        Turn your documents into an AI <br/>
                        <span className="text-indigo-400 font-medium">you can talk to.</span>
                    </motion.p>
                </div>

                {/* Main Action Area */}
                <div className="w-full flex flex-col items-center">
                    <GoogleSignInButton 
                        onGoogleResponse={handleGoogleResponse}
                        loading={status === 'loading' || isSubmitting}
                    />

                    <div className="flex items-center w-full gap-3 mt-5 mb-5">
                        <div className="flex-1 h-px bg-white/10"></div>
                        <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">or continue with email</span>
                        <div className="flex-1 h-px bg-white/10"></div>
                    </div>

                    <form onSubmit={handleManualAuth} className="w-full space-y-4">
                        <AnimatePresence mode="popLayout">
                            {!isLoginMode && (
                                <motion.div 
                                    initial={{ opacity: 0, height: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, height: 'auto', scale: 1 }}
                                    exit={{ opacity: 0, height: 0, scale: 0.95 }}
                                    transition={{ duration: 0.2 }}
                                    className="relative"
                                >
                                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input 
                                        type="text" 
                                        placeholder="Full Name" 
                                        required={!isLoginMode}
                                        value={name}
                                        onChange={e => setName(e.target.value)}
                                        className="w-full input-field pl-10 h-11"
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="relative">
                            <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            <input 
                                type="email" 
                                placeholder="Email address" 
                                required
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                className="w-full input-field pl-10 h-11"
                            />
                        </div>

                        <div className="relative">
                            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                            <input 
                                type="password" 
                                placeholder="Password" 
                                required
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                className="w-full input-field pl-10 h-11"
                            />
                        </div>

                        <button 
                            type="submit" 
                            disabled={status === 'loading' || isSubmitting}
                            className="w-full btn-primary h-11 mt-2 text-sm"
                        >
                            {isSubmitting ? (
                                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                            ) : isLoginMode ? (
                                <>Sign In <LogIn className="w-4 h-4" /></>
                            ) : (
                                <>Create Account <UserPlus className="w-4 h-4" /></>
                            )}
                        </button>
                    </form>

                    <div className="text-center text-xs text-gray-400 pt-5 pb-2">
                        {isLoginMode ? "Don't have an account? " : "Already have an account? "}
                        <button 
                            type="button" 
                            onClick={() => setIsLoginMode(!isLoginMode)}
                            className="text-indigo-400 font-semibold hover:text-indigo-300 transition-colors"
                        >
                            {isLoginMode ? "Sign up" : "Log in"}
                        </button>
                    </div>

                    {/* Trust Signals */}
                    <div className="flex flex-col items-center gap-4 pt-5 mt-2 border-t border-white/5 w-full">
                        <div className="flex items-center gap-2 text-[10px] font-medium text-gray-500 uppercase tracking-widest">
                            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400/70" />
                            Secure End-to-End Encryption
                        </div>
                    </div>
                </div>

                {/* Footer Micro-Interactions */}
                <div className="mt-8 flex items-center justify-between w-full text-[10px] text-gray-600 font-semibold px-2">
                    <span className="hover:text-gray-400 cursor-pointer transition-colors">Privacy Policy</span>
                    <span className="w-1 h-1 bg-gray-800 rounded-full" />
                    <span className="hover:text-gray-400 cursor-pointer transition-colors">Terms of Service</span>
                </div>
            </motion.div>

            {/* Micro-Interaction: Bottom Glow */}
            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="absolute bottom-6 text-gray-700 flex items-center gap-2 text-xs font-medium"
            >
                Built for researchers and professional teams
                <MoveRight className="w-4 h-4 opacity-50" />
            </motion.div>
        </div>
    );
};

export default AuthPage;
