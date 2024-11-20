from supabase import create_client, Client
import streamlit as st
import re

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Enhanced Custom CSS with Background and More Visual Elements
st.markdown("""
    <style>
        /* Background and Global Styling */
        .stApp {
            background: linear-gradient(135deg, #f6f8fc 0%, #e9ecf1 100%);
            background-attachment: fixed;
        }

        /* Animated Background Particles */
        @keyframes particle-animation {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-100vh) rotate(360deg); }
        }

        .background-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 50%;
            animation: particle-animation linear infinite;
        }

        /* Container Styling */
        .main-container {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }

        /* Title Styling */
        .title {
            color: #2c3e50;
            text-align: center;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #3498db, #2980b9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* SQL Editor Styling */
        .sql-editor {
            font-family: 'Fira Code', 'Courier New', monospace;
            background-color: #ffffff;
            border: 1px solid #e0e4e8;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            white-space: pre-wrap;
            line-height: 1.6;
            transition: all 0.3s ease;
        }

        .sql-editor:hover {
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-3px);
        }

        /* Additional Visual Enhancements */
        .stTextArea>div>div>textarea {
            border: 2px solid #3498db;
            border-radius: 8px;
        }

        .stButton>button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            transition: all 0.3s ease;
            font-weight: 600;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
        }

        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
    </style>
""", unsafe_allow_html=True)

# Animated Background Particles Script
st.markdown("""
    <script>
        function createParticles() {
            const particlesContainer = document.createElement('div');
            particlesContainer.className = 'background-particles';
            document.body.appendChild(particlesContainer);

            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.width = `${Math.random() * 20 + 5}px`;
                particle.style.height = particle.style.width;
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.animationDuration = `${Math.random() * 20 + 10}s`;
                particle.style.animationDelay = `${Math.random() * 10}s`;
                particlesContainer.appendChild(particle);
            }
        }
        createParticles();
    </script>
""", unsafe_allow_html=True)

# Rest of the previous code remains the same, wrapped in a main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# [Previous code stays the same, just placed inside this container]

st.markdown('</div>', unsafe_allow_html=True)