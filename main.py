import os
import time
import threading
import streamlit as st
import requests
from dotenv import load_dotenv

# Configure Streamlit for cloud deployment
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Detection", 
    page_icon="🌿", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)


# Enhanced modern CSS
st.markdown(
    """
    <style>
    :root {
        /* Yellow-Blue Pastel Light Summer Sky Happy Color Scheme */
        --yellow-light: rgb(255, 242, 198);      /* light yellow/cream */
        --yellow-lighter: rgb(255, 248, 222);   /* very light yellow/cream */
        --blue-light: rgb(170, 196, 245);        /* light blue */
        --blue-medium: rgb(140, 169, 255);     /* medium blue */
        
        /* Updated brand palette using new colors */
        --primary: rgb(140, 169, 255);          /* medium blue */
        --primary-strong: rgb(100, 140, 220);   /* darker blue for contrast */
        --success: rgb(170, 196, 245);          /* light blue */
        --accent: rgb(255, 242, 198);           /* light yellow */
        --highlight: rgb(255, 248, 222);       /* very light yellow */
        --muted: rgb(120, 140, 180);
        --card-bg: rgba(255, 248, 222, 0.98);
        --chip-bg: rgb(255, 242, 198);
        --shadow: 0 6px 24px rgba(140, 169, 255, 0.2);
        --shadow-lg: 0 14px 42px rgba(140, 169, 255, 0.3);
        --radius: 18px;
        
        /* Professional typography */
        --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        --font-weight-light: 300;
        --font-weight-normal: 400;
        --font-weight-medium: 500;
        --font-weight-semibold: 600;
        --font-weight-bold: 700;
        --font-weight-extrabold: 800;
        
        /* Professional spacing system */
        --space-xs: 4px;
        --space-sm: 8px;
        --space-md: 16px;
        --space-lg: 24px;
        --space-xl: 32px;
        --space-2xl: 48px;
        
        /* Professional transitions */
        --transition-fast: 0.15s ease;
        --transition-normal: 0.25s ease;
        --transition-slow: 0.35s ease;
    }
    /* Professional base styles */
    * { box-sizing: border-box; }
    body { font-family: var(--font-primary); line-height: 1.6; }
    
    /* Enhanced background with yellow-blue pastel gradient and animation */
    .stApp {
        background: linear-gradient(135deg, rgb(255, 248, 222) 0%, rgb(255, 242, 198) 30%, rgb(170, 196, 245) 70%, rgb(140, 169, 255) 100%);
        min-height: 100vh;
        position: relative;
        animation: backgroundShift 15s ease infinite;
    }
    @keyframes backgroundShift {
        0%, 100% { 
            background: linear-gradient(135deg, rgb(255, 248, 222) 0%, rgb(255, 242, 198) 30%, rgb(170, 196, 245) 70%, rgb(140, 169, 255) 100%);
        }
        50% { 
            background: linear-gradient(135deg, rgb(170, 196, 245) 0%, rgb(140, 169, 255) 30%, rgb(255, 242, 198) 70%, rgb(255, 248, 222) 100%);
        }
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(255, 242, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(170, 196, 245, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(255, 248, 222, 0.2) 0%, transparent 60%);
        pointer-events: none;
        z-index: -1;
        animation: floatClouds 20s ease-in-out infinite;
    }
    @keyframes floatClouds {
        0%, 100% { transform: translateY(0) translateX(0); }
        50% { transform: translateY(-20px) translateX(10px); }
    }
    
    /* Professional container system */
    .container-card { background: transparent; border: none; box-shadow: none; padding: 0; }
    .container-card:hover { box-shadow: none; }
    .result-card { background: transparent; border: none; box-shadow: none; padding: 0; margin: var(--space-md) 0; }
    
    /* Enhanced typography hierarchy */
    .disease-title {
        color: var(--primary); 
        font-size: 2.2rem; 
        font-weight: var(--font-weight-extrabold); 
        margin: var(--space-sm) 0 var(--space-md); 
        letter-spacing: -0.02em;
        line-height: 1.2;
        animation: fadeInUp 0.6s ease;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .section-title {
        color: var(--primary); 
        font-size: 1.2rem; 
        font-weight: var(--font-weight-semibold); 
        margin: var(--space-lg) 0 var(--space-sm); 
        letter-spacing: 0.01em;
    }
    .timestamp {
        color: var(--muted); 
        font-size: 0.9rem; 
        margin-top: var(--space-md); 
        text-align: right;
        font-weight: var(--font-weight-medium);
    }
    .info-badge {
        display: inline-block;
        background: var(--chip-bg); 
        color: var(--primary-strong); 
        border-radius: 12px; 
        padding: var(--space-sm) var(--space-md); 
        font-size: 0.9rem; 
        margin: 0 var(--space-sm) var(--space-sm) 0; 
        border: 1px solid rgba(140, 169, 255, 0.3);
        font-weight: var(--font-weight-medium);
        transition: var(--transition-fast);
        animation: pulseBadge 2s ease infinite;
    }
    @keyframes pulseBadge {
        0%, 100% { transform: scale(1); box-shadow: 0 2px 8px rgba(140, 169, 255, 0.2); }
        50% { transform: scale(1.05); box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3); }
    }
    .info-badge:hover { transform: translateY(-1px) scale(1.05); box-shadow: 0 4px 12px rgba(140, 169, 255, 0.25); }
    
    /* Professional hero section */
    .hero { 
        text-align: center; 
        padding: var(--space-2xl) 0 var(--space-xl); 
        position: relative;
        animation: fadeIn 0.8s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .hero h1 { 
        color: var(--primary); 
        margin: 0; 
        font-size: 2.8rem; 
        font-weight: var(--font-weight-extrabold);
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: var(--space-md);
        text-shadow: 0 2px 10px rgba(140, 169, 255, 0.2);
    }
    .hero p { 
        color: var(--muted); 
        margin: 0 0 var(--space-lg); 
        font-size: 1.1rem; 
        font-weight: var(--font-weight-normal);
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .leaf-badge { 
        font-size: 2.4rem; 
        display: inline-block; 
        animation: leafFloat 4s ease-in-out infinite;
        margin-bottom: var(--space-md);
        filter: drop-shadow(0 4px 8px rgba(140, 169, 255, 0.3));
    }
    @keyframes leafFloat { 
        0%, 100% { transform: translateY(0) rotate(0deg); } 
        50% { transform: translateY(-8px) rotate(-5deg); } 
    }
    .trust-badges { 
        margin-top: var(--space-lg); 
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: var(--space-sm);
    }
    .trust-badges .tb { 
        display: inline-block; 
        padding: var(--space-sm) var(--space-md); 
        border-radius: 999px; 
        background: rgba(255, 248, 222, 0.9); 
        border: 1px solid rgba(140, 169, 255, 0.3); 
        color: var(--primary-strong); 
        font-size: 0.9rem; 
        font-weight: var(--font-weight-medium);
        transition: var(--transition-fast);
        backdrop-filter: blur(8px);
        box-shadow: 0 2px 8px rgba(140, 169, 255, 0.15);
    }
    .trust-badges .tb:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 8px 20px rgba(140, 169, 255, 0.25);
        background: rgba(255, 242, 198, 0.95);
    }

    /* Split hero like reference */
    .hero-split { max-width: 1100px; margin: 6px auto 12px; display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; align-items: center; }
    .hero-left { 
        background: linear-gradient(180deg, rgba(140, 169, 255, 0.9), rgba(170, 196, 245, 0.8)); 
        color: #fff; 
        padding: 26px 28px; 
        border-radius: 18px; 
        box-shadow: 0 14px 34px rgba(140, 169, 255, 0.3); 
        animation: slideInLeft 0.8s ease; 
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .hero-left h2 { margin:0 0 10px; font-size: 2.1rem; line-height: 1.2; font-weight: 900; letter-spacing:.4px; }
    .hero-left p { margin:0 0 16px; opacity:.95 }
    .cta { 
        display:inline-block; 
        background: linear-gradient(135deg, rgb(255, 242, 198), rgb(255, 248, 222)); 
        color: rgb(100, 140, 220); 
        font-weight:800; 
        padding:10px 14px; 
        border-radius: 12px; 
        text-decoration:none; 
        box-shadow: 0 8px 18px rgba(255, 242, 198, 0.4); 
        transition: all 0.3s ease; 
    }
    .cta:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 12px 24px rgba(255, 242, 198, 0.5); 
        background: linear-gradient(135deg, rgb(255, 248, 222), rgb(255, 242, 198));
    }
    .hero-right { 
        border-radius: 18px; 
        background: radial-gradient(1200px 120px at 30% 0%, rgba(255, 248, 222, 0.5), rgba(255, 248, 222, 0)), 
                    linear-gradient(135deg, rgb(255, 242, 198) 0%, rgb(170, 196, 245) 100%); 
        box-shadow: 0 14px 34px rgba(140, 169, 255, 0.2); 
        display:grid; 
        place-items:center; 
        min-height: 140px; 
        animation: slideInRight 0.8s ease; 
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .hero-right .vase { font-size: 44px; filter: drop-shadow(0 6px 12px rgba(140, 169, 255, 0.3)); }

    /* Features row */
    .features { max-width: 1100px; margin: 6px auto 6px; display:grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .feature { 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); 
        color: var(--primary-strong); 
        padding: 16px; 
        border-radius: 16px; 
        box-shadow: 0 10px 26px rgba(140, 169, 255, 0.2); 
        display:flex; 
        gap:10px; 
        align-items: center; 
        transition: all 0.3s ease; 
        border: 1px solid rgba(170, 196, 245, 0.3);
    }
    .feature:hover { 
        transform: translateY(-4px); 
        box-shadow: 0 14px 32px rgba(140, 169, 255, 0.3); 
        background: linear-gradient(135deg, rgba(255, 242, 198, 1), rgba(170, 196, 245, 0.9));
    }
    .feature .i { 
        width:34px; 
        height:34px; 
        border-radius:10px; 
        display:grid; 
        place-items:center; 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color:#fff; 
        font-weight:900; 
        animation: pulse 2s ease infinite; 
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    .feature .t { font-weight:800; }
    html { scroll-behavior: smooth; }

    /* Hide Streamlit default toolbar (Deploy and overflow menu) */
    div[data-testid="stToolbar"],
    div[data-testid="stMainMenu"],
    header [data-testid="baseButton-headerNoPadding"],
    header button[kind="header"] { display: none !important; }

    /* Remove white header background and fill top with app background */
    header[data-testid="stHeader"] { background: transparent !important; }
    div[data-testid="stDecoration"] { background: transparent !important; }
    .block-container { padding-top: 68px; }

    /* Replace with a minimal professional status pill */
    .custom-top { 
        position: fixed; 
        top: 8px; 
        right: 14px; 
        z-index: 1000; 
        background: rgba(255, 248, 222, 0.9); 
        border:1px solid rgba(140, 169, 255, 0.3); 
        padding: 6px 10px; 
        border-radius: 999px; 
        font-size:.85rem; 
        color: var(--primary-strong); 
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.2); 
        backdrop-filter: blur(4px); 
    }
    .custom-top .dot { display:inline-block; width:8px; height:8px; border-radius:999px; background:rgb(140, 169, 255); margin-right:8px; animation: pulseDot 2s ease infinite; }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.2); }
    }

    /* Professional header */
    .custom-header { 
        position: fixed; 
        top: 0; 
        left: 0; 
        right: 0; 
        height: 64px; 
        z-index: 999; 
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
        padding: 0 var(--space-lg); 
        backdrop-filter: blur(12px); 
        background: linear-gradient(90deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); 
        border-bottom: 1px solid rgba(140, 169, 255, 0.3); 
        box-shadow: 0 4px 20px rgba(140, 169, 255, 0.2);
        transition: var(--transition-normal);
        animation: slideDown 0.5s ease;
    }
    @keyframes slideDown {
        from { transform: translateY(-100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .custom-header .brand { 
        display: flex; 
        align-items: center; 
        gap: var(--space-md); 
        font-weight: var(--font-weight-extrabold); 
        color: var(--primary-strong);
        font-size: 1.1rem;
        letter-spacing: -0.01em;
    }
    .custom-header .brand .logo { 
        width: 32px; 
        height: 32px; 
        border-radius: 10px; 
        display: grid; 
        place-items: center; 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color: #fff;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3);
        animation: logoSpin 3s ease infinite;
    }
    @keyframes logoSpin {
        0%, 100% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(5deg) scale(1.1); }
    }
    .custom-header .nav { 
        display: flex; 
        gap: var(--space-sm);
    }
    .custom-header .nav .btn { 
        color: var(--primary-strong); 
        text-decoration: none; 
        font-weight: var(--font-weight-semibold); 
        padding: var(--space-sm) var(--space-md); 
        border-radius: 999px; 
        border: 1px solid rgba(140, 169, 255, 0.3); 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.9), rgba(255, 242, 198, 0.8)); 
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.15);
        transition: var(--transition-fast);
        font-size: 0.9rem;
        letter-spacing: 0.01em;
    }
    .custom-header .nav .btn:hover { 
        background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(170, 196, 245, 0.8)); 
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(140, 169, 255, 0.25);
    }
    /* Ensure anchor sections are not hidden behind fixed header */
    #detect, #features, #about, #footer, #detect-desc, #features-desc, #detect-card, #features-card { scroll-margin-top: 72px; }

    /* Sections: Detect & Features content */
    .steps { max-width: 1100px; margin: 18px auto 6px; display:grid; grid-template-columns: repeat(3,1fr); gap: 14px; }
    .step { 
        background:rgba(255, 248, 222, 0.9); 
        border:1px solid rgba(140, 169, 255, 0.3); 
        border-radius:16px; 
        padding:14px; 
        box-shadow:0 10px 22px rgba(140, 169, 255, 0.15); 
        transition: all 0.3s ease; 
    }
    .step:hover { 
        transform: translateY(-4px); 
        box-shadow:0 14px 28px rgba(140, 169, 255, 0.25); 
        background: rgba(255, 242, 198, 0.95);
    }
    .step .sicon { 
        width:34px; 
        height:34px; 
        border-radius:10px; 
        display:grid; 
        place-items:center; 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color:#fff; 
        font-weight:900; 
        margin-bottom:6px; 
        animation: iconBounce 2s ease infinite; 
    }
    @keyframes iconBounce {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.1) rotate(5deg); }
    }
    .step .stitle { font-weight:900; color: var(--primary-strong); margin-bottom:4px; }

    .info-cards { max-width: 1100px; margin: 6px auto 6px; display:grid; grid-template-columns: repeat(4,1fr); gap: 14px; }
    .info-card { 
        background: rgba(255, 248, 222, 0.9); 
        border:1px solid rgba(140, 169, 255, 0.3); 
        border-radius:16px; 
        padding:14px; 
        box-shadow:0 10px 22px rgba(140, 169, 255, 0.15); 
        transition: all 0.3s ease; 
    }
    .info-card:hover { 
        transform: translateY(-3px); 
        box-shadow:0 14px 28px rgba(140, 169, 255, 0.25); 
        background: rgba(255, 242, 198, 0.95);
    }
    .info-card .ic-title { font-weight:900; color: var(--primary-strong); margin-bottom:4px; }
    
    /* Professional collapsible blocks with new colors */
    .collapsible { 
        max-width: 1100px; 
        margin: var(--space-lg) auto; 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); 
        border: 1px solid rgba(140, 169, 255, 0.3); 
        border-radius: 20px; 
        box-shadow: 0 8px 32px rgba(140, 169, 255, 0.2); 
        color: var(--primary-strong); 
        overflow: hidden;
        transition: var(--transition-normal);
        backdrop-filter: blur(8px);
        position: relative;
    }
    .collapsible::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, rgb(170, 196, 245), rgb(255, 242, 198), rgb(140, 169, 255));
        animation: gradientShift 3s ease infinite;
    }
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    .collapsible:hover { 
        box-shadow: 0 12px 40px rgba(140, 169, 255, 0.3);
        transform: translateY(-3px);
        background: linear-gradient(135deg, rgba(255, 242, 198, 1), rgba(170, 196, 245, 0.9));
    }
    .collapsible input[type="checkbox"] { display: none; }
    .collapsible .title { 
        padding: var(--space-lg) var(--space-xl); 
        font-weight: var(--font-weight-extrabold); 
        color: var(--primary-strong); 
        cursor: pointer; 
        user-select: none; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        font-size: 1.1rem;
        letter-spacing: 0.01em;
        transition: var(--transition-fast);
        position: relative;
        z-index: 1;
    }
    .collapsible .title:hover { 
        background: rgba(140, 169, 255, 0.1); 
        color: var(--primary);
    }
    .collapsible .title::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, rgb(170, 196, 245), rgb(255, 242, 198));
        border-radius: 2px;
        opacity: 0.8;
    }
    .collapsible .title::after { 
        content: '▼'; 
        transition: var(--transition-normal); 
        font-size: 0.9rem;
        opacity: 0.7;
    }
    .collapsible input[type="checkbox"]:checked + .title::after { 
        transform: rotate(180deg); 
        opacity: 1;
    }
    .collapsible .content { 
        max-height: 0; 
        overflow: hidden; 
        transition: max-height var(--transition-slow) ease; 
        padding: 0 var(--space-xl); 
    }
    .collapsible input[type="checkbox"]:checked ~ .content { 
        max-height: 800px; 
        padding-bottom: var(--space-xl); 
    }
    
    /* Modern Footer Design - Clean and Elegant */
    .footer { 
        background: linear-gradient(180deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)) !important; 
        color: #333333 !important; 
        margin-top: 80px; 
        padding: 60px 20px 40px; 
        border-top: 4px solid rgba(140, 169, 255, 0.3);
        box-shadow: 0 -4px 20px rgba(140, 169, 255, 0.15);
        position: relative;
    }
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, rgb(140, 169, 255), rgb(170, 196, 245), rgb(140, 169, 255));
    }
    .footer-container { 
        max-width: 1200px; 
        margin: 0 auto; 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
        gap: 40px; 
        margin-bottom: 40px; 
    }
    .footer-section h3 { 
        color: rgb(100, 140, 220) !important; 
        font-weight: 800 !important; 
        font-size: 1.3rem !important; 
        margin-bottom: 20px; 
        display: flex; 
        align-items: center; 
        gap: 10px; 
        letter-spacing: 0.3px;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(140, 169, 255, 0.2);
    }
    .footer-section h3::before {
        content: '';
        width: 5px;
        height: 24px;
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245));
        border-radius: 3px;
        box-shadow: 0 2px 6px rgba(140, 169, 255, 0.3);
    }
    .footer-section p, .footer-section a { 
        color: rgb(80, 100, 140) !important; 
        line-height: 1.8 !important; 
        text-decoration: none !important; 
        transition: all 0.3s ease;
        display: block;
        margin-bottom: 12px;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    .footer-section a:hover { 
        color: rgb(140, 169, 255) !important; 
        transform: translateX(8px);
        font-weight: 600 !important;
        padding-left: 8px;
    }
    .footer-section a::before {
        content: '→';
        margin-right: 6px;
        opacity: 0;
        transition: all 0.3s ease;
    }
    .footer-section a:hover::before {
        opacity: 1;
        margin-right: 8px;
    }
    .footer-brand { 
        display: flex; 
        align-items: center; 
        gap: 12px; 
        margin-bottom: 20px; 
    }
    .footer-brand .logo { 
        width: 50px; 
        height: 50px; 
        display: grid; 
        place-items: center; 
        border-radius: 14px; 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color: #ffffff !important; 
        font-size: 1.6rem; 
        box-shadow: 0 4px 16px rgba(140, 169, 255, 0.4);
        transition: all 0.3s ease;
    }
    .footer-brand:hover .logo {
        transform: rotate(5deg) scale(1.05);
        box-shadow: 0 6px 20px rgba(140, 169, 255, 0.5);
    }
    .footer-brand .name { 
        font-weight: 800 !important; 
        font-size: 1.5rem !important; 
        color: rgb(100, 140, 220) !important; 
        letter-spacing: 0.5px;
    }
    .footer-social { 
        display: flex; 
        gap: 12px; 
        margin-top: 20px; 
        flex-wrap: wrap;
    }
    .footer-social a { 
        width: 44px; 
        height: 44px; 
        border-radius: 12px; 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)) !important; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: rgb(140, 169, 255) !important; 
        transition: all 0.3s ease; 
        border: 2px solid rgba(140, 169, 255, 0.3); 
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.2); 
        text-decoration: none;
    }
    .footer-social a svg {
        width: 20px;
        height: 20px;
        fill: currentColor;
        transition: all 0.3s ease;
    }
    .footer-social a:hover { 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)) !important; 
        transform: translateY(-4px) scale(1.1); 
        box-shadow: 0 6px 20px rgba(140, 169, 255, 0.4); 
        color: #ffffff !important; 
        border-color: rgba(140, 169, 255, 0.5); 
    }
    .footer-social a:hover svg {
        transform: scale(1.1);
    }
    .footer-bottom { 
        border-top: 2px solid rgba(140, 169, 255, 0.2) !important; 
        padding-top: 30px; 
        margin-top: 40px;
        text-align: center; 
        color: rgb(100, 120, 160) !important; 
        font-size: 0.95rem !important; 
        font-weight: 500 !important;
    }
    .footer-bottom .copyright { 
        margin-bottom: 10px; 
    }
    .footer-bottom .links { 
        display: flex; 
        justify-content: center; 
        gap: 20px; 
        flex-wrap: wrap; 
    }
    .footer-bottom .links a { 
        color: rgb(100, 140, 220) !important; 
        text-decoration: none !important; 
        transition: all 0.3s ease;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 6px 12px;
        border-radius: 8px;
        position: relative;
    }
    .footer-bottom .links a:hover { 
        color: rgb(140, 169, 255) !important; 
        font-weight: 600 !important;
        background: rgba(140, 169, 255, 0.1);
    }
    .footer-bottom .links a::after {
        content: '•';
        margin: 0 8px;
        color: rgba(140, 169, 255, 0.3);
    }
    .footer-bottom .links a:last-child::after {
        display: none;
    }
    
    /* Unique floating action button with leaf animation */
    .floating-action {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245));
        box-shadow: 0 8px 24px rgba(140, 169, 255, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: var(--transition-normal);
        z-index: 1000;
        overflow: hidden;
        animation: floatBounce 3s ease-in-out infinite;
    }
    @keyframes floatBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .floating-action::before {
        content: '🌿';
        font-size: 1.8rem;
        animation: leafSpin 3s ease-in-out infinite;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    .floating-action::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 248, 222, 0.4) 0%, transparent 70%);
        animation: ripple 2s ease-in-out infinite;
        pointer-events: none;
    }
    .floating-action:hover {
        transform: scale(1.1) translateY(-2px);
        box-shadow: 0 12px 32px rgba(140, 169, 255, 0.5);
    }
    .floating-action:active {
        transform: scale(0.95);
    }
    @keyframes leafSpin {
        0%, 100% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(-10deg) scale(1.1); }
        50% { transform: rotate(0deg) scale(1.2); }
        75% { transform: rotate(10deg) scale(1.1); }
    }
    @keyframes ripple {
        0% { transform: scale(0); opacity: 1; }
        100% { transform: scale(1); opacity: 0; }
    }
    
    /* Chatbot Q&A Modal */
    .chatbot-modal {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 380px;
        max-height: 600px;
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.98), rgba(255, 242, 198, 0.98));
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(140, 169, 255, 0.4);
        backdrop-filter: blur(12px);
        border: 2px solid rgba(170, 196, 245, 0.4);
        z-index: 1001;
        transform: translateY(20px) scale(0.9);
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        overflow: hidden;
        display: none;
    }
    .chatbot-modal.show {
        transform: translateY(0) scale(1);
        opacity: 1;
        display: block;
    }
    .chatbot-toggle:checked ~ .chatbot-modal {
        display: block;
        transform: translateY(0) scale(1);
        opacity: 1;
    }
    .chatbot-header {
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245));
        color: white;
        padding: 18px 22px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3);
    }
    .chatbot-header .icon {
        width: 24px;
        height: 24px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
    }
    .chatbot-content {
        padding: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    .chatbot-question {
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.3), rgba(255, 242, 198, 0.3)); 
        border: 1px solid rgba(140, 169, 255, 0.3); 
        border-radius: 12px; 
        margin-bottom: 12px; 
        overflow: hidden;
        transition: all 0.3s ease;
        font-weight: 600;
        color: var(--primary-strong);
    }
    .chatbot-question label {
        cursor: pointer;
        display: block;
        font-weight: 600;
        color: var(--primary-strong);
    }
    .chatbot-question:hover {
        background: linear-gradient(135deg, rgba(255, 242, 198, 0.4), rgba(170, 196, 245, 0.3));
        transform: translateX(6px);
        box-shadow: 0 6px 16px rgba(140, 169, 255, 0.25);
        border-color: rgba(170, 196, 245, 0.5);
    }
    .chatbot-answer {
        background: rgba(255, 248, 222, 0.9);
        border: 1px solid rgba(140, 169, 255, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin-top: 8px;
        font-size: 0.9rem;
        line-height: 1.5;
        color: var(--muted);
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }
    .chatbot-question input:checked ~ .chatbot-answer {
        max-height: 200px;
        animation: slideDown 0.3s ease;
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chatbot-close {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 24px;
        height: 24px;
        background: rgba(255,255,255,0.2);
        border: none;
        border-radius: 50%;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
    }
    .upload-preview { border-radius: 14px; overflow: hidden; box-shadow: var(--shadow); }
    /* Center the uploader card and style Streamlit widgets */
    .center-wrap { max-width: 880px; margin: 0 auto; }
    .stButton>button { 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color: #fff; 
        border: 0; 
        padding: 10px 14px; 
        border-radius: 10px; 
        font-weight: 700; 
        box-shadow: var(--shadow); 
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, rgb(170, 196, 245), rgb(140, 169, 255)); 
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(140, 169, 255, 0.4);
    }
    .success-icon { font-size: 1.3rem; margin-right: 6px; }
    /* Hide any stray Streamlit input widget that renders as a blank white bar */
    div[data-testid="stTextInput"], .stTextInput, .stTextInput input,
    div[data-testid="stTextArea"], .stTextArea, .stTextArea textarea,
    .stApp input[type="text"], .stApp textarea,
    .stApp [data-baseweb="input"], .stApp [data-baseweb="textarea"],
    .stApp div[role="textbox"] {
        display: none !important; height: 0 !important; padding: 0 !important; margin: 0 !important; border: 0 !important; box-shadow: none !important; background: transparent !important;
    }
    /* Ensure top block has no stray spacing */
    .block-container > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }
    /* Tighten top spacing above the uploader title */
    .center-wrap .container-card { margin-top: 0; }

    /* --- File Uploader Pro Styling --- */
    [data-testid="stFileUploader"] { margin-top: 6px; }
    [data-testid="stFileUploaderDropzone"] {
        position: relative;
        background: transparent !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 10px 0 !important;
        box-shadow: none !important;
        transition: border-color .2s ease, box-shadow .2s ease, transform .05s ease;
        overflow: hidden;
        isolation: isolate;
    }
    /* Force all inner nodes in dropzone to be transparent */
    [data-testid="stFileUploaderDropzone"] * {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    /* animated subtle gradient border */
    [data-testid="stFileUploaderDropzone"]::before { content: none; }
    @keyframes borderShift { to { background-position: 200% 0; } }
    [data-testid="stFileUploaderDropzone"]:hover { box-shadow: none !important; transform: none !important; }
    /* Title and helper text inside dropzone */
    [data-testid="stFileUploaderDropzone"] p:first-child { color: var(--primary-strong) !important; font-weight: 800 !important; margin-bottom: 4px !important; }
    [data-testid="stFileUploaderDropzone"] p:nth-child(2) { color: var(--muted) !important; font-size: .9rem !important; }
    /* Cloud icon */
    [data-testid="stFileUploaderDropzone"] svg { color: var(--primary) !important; opacity: .9; }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, rgb(140, 169, 255) 0%, rgb(170, 196, 245) 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 8px 14px !important;
        font-weight: 700 !important;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"] button:hover { 
        filter: brightness(1.1); 
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(140, 169, 255, 0.4);
    }
    /* filename row */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        background: rgba(255, 248, 222, 0.95);
        border: 1px solid rgba(140, 169, 255, 0.3);
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 4px 14px rgba(140, 169, 255, 0.15);
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] p { margin:0; font-weight: 600; color: var(--primary-strong); }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] small { color: var(--muted); }
    /* remove icon */
    [data-testid="stFileUploader"] svg[aria-label="close"] { color: #fff; background: var(--primary); border-radius: 8px; padding: 4px; box-shadow: 0 2px 6px rgba(0,0,0,.15); }
    [data-testid="stFileUploader"] svg[aria-label="close"]:hover { background: var(--primary-strong); }
    /* Image preview card */
    img[alt^="uploaded"] { border-radius: 16px; box-shadow: 0 12px 30px rgba(140, 169, 255, 0.25); }

    /* helper chips */
    .helper-chips { margin: 6px 2px 2px; }
    .helper-chips .chip { 
        display:inline-block; 
        padding:6px 12px; 
        border-radius:999px; 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.95) 0%, rgba(255, 242, 198, 0.95) 100%); 
        border:1px solid rgba(140, 169, 255, 0.3); 
        color: var(--primary-strong); 
        margin-right:10px; 
        font-size:.85rem; 
        font-weight:700; 
        letter-spacing:.2px; 
        box-shadow: 0 3px 10px rgba(140, 169, 255, 0.15); 
    }

    /* skeleton placeholder */
    .skeleton { 
        height: 140px; 
        border-radius: 16px; 
        background: linear-gradient(90deg, rgba(255, 248, 222, 0.5), rgba(255, 242, 198, 0.3), rgba(255, 248, 222, 0.5)); 
        background-size: 200% 100%; 
        animation: shimmer 1.2s linear infinite; 
        margin: 8px 0; 
    }
    @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

    /* colorful progress bar & spinner */
    [data-testid="stProgressBar"] div[role="progressbar"] {
        background: linear-gradient(90deg, rgb(140, 169, 255), rgb(170, 196, 245), rgb(255, 242, 198), rgb(140, 169, 255));
        background-size: 300% 100%;
        animation: pbmove 2s linear infinite;
        border-radius: 999px;
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.25);
        height: 10px;
    }
    @keyframes pbmove { 0% { background-position: 0% 0; } 100% { background-position: 300% 0; } }
    [data-testid="stProgressBar"] > div { background: rgba(255, 248, 222, 0.5); border-radius: 999px; }
    [data-testid="stSpinner"] { filter: hue-rotate(200deg) saturate(1.2); }

    /* Preview frame with gradient border */
    .preview-frame { position: relative; border-radius: 18px; padding: 6px; }
    .preview-frame::before { 
        content:""; 
        position:absolute; 
        inset:0; 
        border-radius:18px; 
        padding:2px; 
        background: linear-gradient(135deg, rgb(170, 196, 245), rgb(140, 169, 255)); 
        -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); 
        -webkit-mask-composite: xor; 
        mask-composite: exclude; 
    }

    /* Professional guidance banner with dual gradient and glass effect */
    .guidance { 
        margin-top: 8px; 
        border-radius: 12px; 
        padding: 12px 14px; 
        display:flex; 
        align-items:center; 
        gap:10px; 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.7), rgba(255, 242, 198, 0.7));
        border: 1px solid rgba(140, 169, 255, 0.3);
        box-shadow: 0 10px 24px rgba(140, 169, 255, 0.15);
        backdrop-filter: blur(6px);
    }
    .guidance .g-icon { 
        width:28px; 
        height:28px; 
        display:grid; 
        place-items:center; 
        border-radius:8px; 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color:#fff; 
        font-weight:900; 
    }
    .guidance .g-text { color:var(--primary-strong); font-weight:700; letter-spacing:.2px; }

    /* Results header pill */
    .results-header { 
        background: transparent; 
        border:none; 
        border-radius:0; 
        padding:0; 
        box-shadow:none; 
        display:flex; 
        align-items:center; 
        gap:10px; 
        margin: 0 0 6px; 
    }
    .results-header .icon { 
        width:24px; 
        height:24px; 
        display:grid; 
        place-items:center; 
        border-radius:6px; 
        background:linear-gradient(135deg, rgb(255, 242, 198), rgb(140, 169, 255)); 
        color:#fff; 
        font-weight:900; 
    }
    .results-header .title { 
        font-weight:900; 
        color: var(--primary-strong); 
        letter-spacing:.4px; 
        text-transform: uppercase; 
        font-size: .95rem; 
    }
    .results-header .pill { 
        margin-left:auto; 
        background: var(--chip-bg); 
        color: var(--primary-strong); 
        padding:3px 8px; 
        border-radius:999px; 
        font-size:.8rem; 
        border:1px solid rgba(140, 169, 255, 0.3); 
    }
    /* Eliminate extra vertical gap before results */
    .stMarkdown div:has(> .results-header) { margin-top: 0 !important; }
    .result-card { margin-top: 4px; }

    /* Section heading style for uploader */
    .section-label { display:flex; align-items:center; gap:10px; margin: 6px 2px 8px; }
    .section-label .dot { 
        width:10px; 
        height:10px; 
        border-radius:50%; 
        background: var(--primary); 
        box-shadow: 0 0 0 4px rgba(140, 169, 255, 0.2); 
        animation: pulseDot 2s ease infinite;
    }
    .section-label h3 { 
        margin:0; 
        font-size: 1.05rem; 
        letter-spacing:.4px; 
        color: var(--primary-strong); 
        font-weight:800; 
        text-transform: uppercase; 
    }
    .section-divider { 
        height:2px; 
        background: linear-gradient(90deg, var(--primary) 0%, transparent 100%); 
        border-radius:2px; 
        margin-top:6px; 
    }

    /* --- Professional polish & consistency --- */
    html { scroll-behavior: smooth; }
    body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
    :root {
        --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px; --space-5: 20px; --space-6: 24px;
        --ring: 0 0 0 3px rgba(255, 242, 198, 0.5);
    }
    .container { max-width: 1120px; margin: 0 auto; padding: 0 var(--space-4); }
    .card { 
        background: rgba(255, 248, 222, 0.95); 
        border: 1px solid rgba(140, 169, 255, 0.25); 
        border-radius: 16px; 
        box-shadow: 0 8px 22px rgba(140, 169, 255, 0.15); 
    }
    .btn:focus-visible, a:focus-visible, button:focus-visible { outline: none; box-shadow: var(--ring); }
    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }

    /* Professional feature tiles with brand colors */
    .features { max-width: 1100px; margin: 8px auto 6px; display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; }
    .features .feature { 
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); 
        border: 1px solid rgba(140, 169, 255, 0.3); 
        border-radius: 16px; 
        padding: 16px; 
        display: flex; 
        gap: 12px; 
        align-items: flex-start; 
        box-shadow: 0 8px 24px rgba(140, 169, 255, 0.15);
        transition: var(--transition-fast);
        position: relative;
        overflow: hidden;
    }
    .features .feature::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, rgb(170, 196, 245), rgb(255, 242, 198));
        animation: gradientShift 3s ease infinite;
    }
    .features .feature:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 12px 32px rgba(140, 169, 255, 0.25);
        background: linear-gradient(135deg, rgba(255, 242, 198, 1), rgba(170, 196, 245, 0.9));
    }
    .features .feature .i { 
        width: 36px; 
        height: 36px; 
        border-radius: 12px; 
        display: grid; 
        place-items: center; 
        background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); 
        color: #fff; 
        font-weight: 900;
        box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3);
        font-size: 1.1rem;
    }
    .features .feature .t { 
        font-weight: var(--font-weight-extrabold); 
        color: var(--primary-strong);
        font-size: 1rem;
        margin-bottom: 4px;
    }
    .features .feature div:last-child {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.4;
        font-weight: var(--font-weight-medium);
    }

    /* Collapsibles: tighter, cleaner */
    .collapsible { backdrop-filter: blur(4px); }
    .collapsible .title { display:flex; align-items:center; gap:10px; }
    .collapsible .title::after { 
        content:""; 
        flex:1; 
        height:1px; 
        background: linear-gradient(90deg, rgba(140, 169, 255, 0.3), rgba(140, 169, 255, 0)); 
        opacity:.6; 
    }

    /* Streamlit scrollbars (subtle) */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-thumb { 
        background: rgba(140, 169, 255, 0.5); 
        border-radius: 999px; 
        border: 2px solid rgba(255, 248, 222, 0.9); 
    }
    ::-webkit-scrollbar-track { background: rgba(255, 248, 222, 0.6); }

    /* Responsive design for all screen sizes */
    @media (max-width: 1200px) {
        .hero-content { max-width: 1000px; }
        .feature-grid { grid-template-columns: repeat(3, 1fr); }
        .upload-area { max-width: 600px; }
        .collapsible { max-width: 900px; }
    }
    
    @media (max-width: 992px) {
        .hero-content { flex-direction: column; text-align: center; max-width: 800px; }
        .hero-text { margin-right: 0; margin-bottom: 20px; }
        .hero-image { max-width: 250px; }
        .feature-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .upload-area { max-width: 500px; }
        .custom-header { padding: 10px 16px; }
        .header-nav { gap: 10px; }
        .collapsible { max-width: 700px; }
    }
    
    @media (max-width: 768px) {
        .hero-content { max-width: 100%; padding: 20px; }
        .hero-text h1 { font-size: 1.8rem; }
        .hero-text p { font-size: 1rem; }
        .hero-image { max-width: 200px; }
        .feature-grid { grid-template-columns: 1fr; gap: 12px; }
        .feature-card { padding: 12px; }
        .upload-area { max-width: 100%; padding: 20px; margin: 0 10px; }
        .upload-content { padding: 20px; }
        .upload-icon { font-size: 2rem; }
        .upload-text { font-size: 0.9rem; }
        .upload-subtext { font-size: 0.8rem; }
        .browse-btn { padding: 8px 16px; font-size: 0.85rem; }
        .upload-chips { flex-direction: column; gap: 6px; }
        .upload-chip { font-size: 0.75rem; padding: 4px 8px; }
        .result-card { padding: 12px; margin: 8px 10px; }
        .disease-title { font-size: 1.1rem; }
        .disease-subtitle { font-size: 0.8rem; }
        .info-badge { font-size: 0.7rem; padding: 3px 6px; }
        .symptom-list, .cause-list, .treatment-list { font-size: 0.85rem; }
        .custom-header { padding: 8px 12px; flex-wrap: wrap; }
        .header-brand { font-size: 1.1rem; }
        .header-nav { gap: 8px; flex-wrap: wrap; }
        .btn { padding: 6px 12px; font-size: 0.8rem; }
        .status-pill { font-size: 0.7rem; padding: 3px 8px; }
        .collapsible { margin: 10px; }
        .footer { padding: 40px 15px 25px; }
        .footer-container { grid-template-columns: 1fr; gap: 30px; }
        .footer-section { text-align: center; }
        .footer-section h3 { justify-content: center; }
        .footer-social { justify-content: center; }
        .footer-bottom .links { flex-direction: column; gap: 10px; }
        
        /* Mobile-specific professional enhancements */
        .hero { padding: 20px 16px; }
        .hero h1 { font-size: 1.6rem; line-height: 1.2; margin-bottom: 8px; }
        .hero p { font-size: 0.95rem; margin-bottom: 16px; }
        .trust-badges { margin-top: 12px; }
        .trust-badges .tb { font-size: 0.8rem; padding: 6px 10px; margin: 0 4px; }
        
        /* Mobile upload area */
        .upload-area { border-radius: 20px; margin: 16px 8px; }
        .upload-content { padding: 24px 16px; }
        .upload-text { font-size: 1rem; font-weight: 700; }
        .upload-subtext { font-size: 0.85rem; margin-top: 8px; }
        .browse-btn { padding: 10px 20px; font-size: 0.9rem; border-radius: 25px; }
        
        /* Mobile collapsible cards */
        .collapsible { margin: 12px 8px; border-radius: 18px; }
        .collapsible .title { padding: 16px 18px; font-size: 1.1rem; }
        .collapsible .content { padding: 0 18px 18px; }
        .collapsible .content > div { grid-template-columns: 1fr !important; gap: 12px; }
        .collapsible .card { padding: 16px; border-radius: 12px; }
        
        /* Mobile features grid */
        .features { grid-template-columns: 1fr; gap: 12px; margin: 16px 8px; }
        .features .feature { padding: 16px; border-radius: 16px; }
        .features .feature .i { width: 36px; height: 36px; font-size: 1.1rem; }
        .features .feature .t { font-size: 1rem; }
        
        /* Mobile header improvements */
        .custom-header { height: 60px; padding: 0 16px; }
        .header-brand { font-size: 1.2rem; }
        .header-nav .btn { padding: 8px 14px; font-size: 0.85rem; border-radius: 20px; }
    }
    
    @media (max-width: 480px) {
        .hero-text h1 { font-size: 1.5rem; }
        .hero-text p { font-size: 0.9rem; }
        .hero-image { max-width: 150px; }
        .upload-area { padding: 15px; margin: 0 5px; }
        .upload-content { padding: 15px; }
        .upload-text { font-size: 0.8rem; }
        .upload-subtext { font-size: 0.7rem; }
        .browse-btn { padding: 6px 12px; font-size: 0.8rem; }
        .custom-header { padding: 6px 8px; }
        .header-brand { font-size: 1rem; }
        .header-nav { gap: 6px; }
        .btn { padding: 5px 10px; font-size: 0.75rem; }
        .status-pill { font-size: 0.65rem; padding: 2px 6px; }
        .collapsible { margin: 5px; }
        .collapsible .title { padding: 10px 12px; font-size: 0.9rem; }
        .collapsible .content { padding: 0 12px; }
        .feature-card { padding: 10px; }
        .feature-card h4 { font-size: 0.9rem; }
        .feature-card p { font-size: 0.8rem; }
        .trust-badges .tb { font-size: 0.75rem; padding: 3px 8px; }
    }
    
    @media (max-width: 360px) {
        .hero-text h1 { font-size: 1.3rem; }
        .hero-text p { font-size: 0.85rem; }
        .upload-area { padding: 12px; margin: 0 3px; }
        .upload-content { padding: 12px; }
        .custom-header { padding: 4px 6px; }
        .header-brand { font-size: 0.9rem; }
        .btn { padding: 4px 8px; font-size: 0.7rem; }
        .collapsible { margin: 3px; }
        .collapsible .title { padding: 8px 10px; font-size: 0.85rem; }
        .collapsible .content { padding: 0 10px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class='custom-header'>
      <div class='brand'>
        <div class='logo'>🌿</div>
        <div>Smart Leaf</div>
      </div>
      <div class='nav'>
        <a class='btn' href='#detect-desc'>Detect</a>
        <a class='btn' href='#features-desc'>Features</a>
        <a class='btn' href='#about'>About</a>
      </div>
    </div>
    <script>
    function initSmoothScroll() {
        // Handle anchor link clicks for smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href.length > 1) {
                    e.preventDefault();
                    const targetId = href.substring(1);
                    // Wait a bit for Streamlit to render content
                    setTimeout(function() {
                        const targetElement = document.getElementById(targetId);
                        if (targetElement) {
                            const headerHeight = 72;
                            const targetPosition = targetElement.offsetTop - headerHeight;
                            window.scrollTo({
                                top: Math.max(0, targetPosition),
                                behavior: 'smooth'
                            });
                        } else {
                            // Fallback: try scrolling to the element by selector
                            const element = document.querySelector('[id="' + targetId + '"]');
                            if (element) {
                                const headerHeight = 72;
                                const targetPosition = element.offsetTop - headerHeight;
                                window.scrollTo({
                                    top: Math.max(0, targetPosition),
                                    behavior: 'smooth'
                                });
                            }
                        }
                    }, 100);
                }
            });
        });
    }
    
    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSmoothScroll);
    } else {
        initSmoothScroll();
    }
    </script>
    <div class='hero'>
        <div class='leaf-badge'>🌿</div>
        <h1>Leaf Disease Detection</h1>
        <p>Upload a leaf image to detect diseases and get expert recommendations.</p>
        <div class='trust-badges'>
          <span class='tb'>Privacy‑safe</span>
          <span class='tb'>~5s analysis</span>
          <span class='tb'>AI powered</span>
        </div>
    </div>
    <div id='detect' class='hero-split'>
      <div class='hero-left'>
        <h2>AI Leaf Disease Detection</h2>
        <p>Analyze plant leaves with Groq Llama Vision. Get disease name, type, severity, confidence and treatment in seconds.</p>
        <a href='#leaf-disease-detection' class='cta'>Start Analysis</a>
      </div>
      <div class='hero-right'>
        <div class='vase'>🧪</div>
      </div>
    </div>
    <div id='features' class='features'>
      <div class='feature'><div class='i'>🔍</div><div><div class='t'>500+ Diseases</div><div>Fungal, bacterial, viral, pests, deficiency</div></div></div>
      <div class='feature'><div class='i'>⚡</div><div><div class='t'>Real‑time</div><div>Typical analysis 2–5 seconds</div></div></div>
      <div class='feature'><div class='i'>📈</div><div><div class='t'>Severity & Confidence</div><div>Actionable, quantified results</div></div></div>
      <div class='feature'><div class='i'>💊</div><div><div class='t'>Treatment Guide</div><div>Practical steps and prevention</div></div></div>
    </div>
    <div id='detect-desc' class='collapsible'>
      <input type='checkbox' id='detect-toggle'>
      <label for='detect-toggle' class='title'>Detect</label>
      <div class='content'>
        <div style='display:grid;grid-template-columns:repeat(2,1fr);gap:12px;'>
          <div class='card' style='padding:12px;'>
            <div style='font-weight:900;color:var(--primary-strong);margin-bottom:6px;'>What it does</div>
            <div>Uploads your leaf photo securely, validates quality and analyzes with Groq Llama Vision to identify diseases.</div>
          </div>
          <div class='card' style='padding:12px;'>
            <div style='font-weight:900;color:var(--primary-strong);margin-bottom:6px;'>About</div>
            <div>Disease name, type (fungal/bacterial/viral/pest/deficiency), severity, confidence and step‑by‑step treatment.</div>
          </div>
        </div>
      </div>
    </div>
    <div id='features-desc' class='collapsible'>
      <input type='checkbox' id='features-toggle'>
      <label for='features-toggle' class='title'>Features</label>
      <div class='content'>
        <div style='display:grid;grid-template-columns:repeat(2,1fr);gap:12px;'>
          <div class='card' style='padding:12px;'>
            <div style='font-weight:900;color:var(--primary-strong);margin-bottom:6px;'>Coverage & Speed</div>
            <div>500+ plant diseases, typical analysis 2–5 seconds, lightweight uploads, mobile‑first experience.</div>
          </div>
          <div class='card' style='padding:12px;'>
            <div style='font-weight:900;color:var(--primary-strong);margin-bottom:6px;'>Explainability</div>
            <div>Extracted symptoms and likely causes with clear treatment actions and prevention tips.</div>
          </div>
        </div>
      </div>
    </div>
    
    """,
    unsafe_allow_html=True,
)

# Prefer API URL from environment with sensible defaults
load_dotenv()
api_url = os.getenv("API_URL") or os.getenv("FASTAPI_URL") or "http://leaf-diseases-detect.vercel.app"

left, center, right = st.columns([1, 3, 1])
with center:
    st.markdown("<div class='center-wrap'>", unsafe_allow_html=True)
    st.markdown("<div class='container-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'><span class='dot'></span><h3>Upload Leaf Image</h3></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    st.markdown("<div class='helper-chips'><span class='chip'>Max 200MB</span><span class='chip'>Formats: JPG, JPEG, PNG</span></div>", unsafe_allow_html=True)
    if uploaded_file is not None:
        st.markdown("<div class='preview-frame'>", unsafe_allow_html=True)
        st.image(uploaded_file, caption="Preview", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        detect_now = st.button("🔍 Detect Disease", use_container_width=True, type="primary")
    else:
        st.info("Drag & drop a JPG or PNG image of a leaf to begin.")
        detect_now = False
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with center:
    if uploaded_file is not None and detect_now:
        if True:
            with st.spinner("Analyzing image and contacting API..."):
                st.markdown("<div class='skeleton'></div>", unsafe_allow_html=True)
                progress = st.progress(0)
                def _animate():
                    for i in range(0, 101, 2):
                        time.sleep(0.03)
                        try:
                            progress.progress(i)
                        except Exception:
                            break
                threading.Thread(target=_animate, daemon=True).start()
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(
                        f"{api_url}/disease-detection-file", files=files)
                    if response.status_code == 200:
                        result = response.json()

                        # Check if it's an invalid image
                        if result.get("disease_type") == "invalid_image":
                            st.markdown("<div class='result-card'>",
                                        unsafe_allow_html=True)
                            st.markdown(
                                "<div class='disease-title'>⚠️ Invalid Image</div>", unsafe_allow_html=True)
                            st.markdown(
                                "<div style='color: #ff5722; font-size: 1.1em; margin-bottom: 1em;'>Please upload a clear image of a plant leaf for accurate disease detection.</div>", unsafe_allow_html=True)

                            # Show the symptoms (which contain the error message)
                            if result.get("symptoms"):
                                st.markdown(
                                    "<div class='section-title'>Issue</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='symptom-list'>",
                                            unsafe_allow_html=True)
                                for symptom in result.get("symptoms", []):
                                    st.markdown(
                                        f"<li>{symptom}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            # Show treatment recommendations
                            if result.get("treatment"):
                                st.markdown(
                                    "<div class='section-title'>What to do</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='treatment-list'>",
                                            unsafe_allow_html=True)
                                for treat in result.get("treatment", []):
                                    st.markdown(
                                        f"<li>{treat}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            st.markdown("</div>", unsafe_allow_html=True)

                        elif result.get("disease_detected"):
                            st.markdown("<div class='results-header'><div class='icon'>🧪</div><div class='title'>Results</div><div class='pill'>AI Analysis</div></div>", unsafe_allow_html=True)
                            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='disease-title'>🦠 {result.get('disease_name', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Type: {result.get('disease_type', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Severity: {result.get('severity', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Symptoms</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='symptom-list'>",
                                        unsafe_allow_html=True)
                            for symptom in result.get("symptoms", []):
                                st.markdown(
                                    f"<li>{symptom}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Possible Causes</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='cause-list'>",
                                        unsafe_allow_html=True)
                            for cause in result.get("possible_causes", []):
                                st.markdown(
                                    f"<li>{cause}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Treatment</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='treatment-list'>",
                                        unsafe_allow_html=True)
                            for treat in result.get("treatment", []):
                                st.markdown(
                                    f"<li>{treat}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='timestamp'>🕒 {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            # Healthy leaf case
                            st.markdown("<div class='results-header'><div class='icon'>🧪</div><div class='title'>Results</div><div class='pill'>AI Analysis</div></div>", unsafe_allow_html=True)
                            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='disease-title'>✅ Healthy Leaf</div>", unsafe_allow_html=True)
                            st.markdown(
                                "<div style='color: #4caf50; font-size: 1.1em; margin-bottom: 1em;'>No disease detected in this leaf. The plant appears to be healthy!</div>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Status: {result.get('disease_type', 'healthy')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Confidence: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='timestamp'>🕒 {result.get('analysis_timestamp', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    elif uploaded_file is None:
        st.markdown("<div class='center-wrap'><div class='container-card'>", unsafe_allow_html=True)
        st.warning("Upload a leaf image above to enable disease detection.")
        st.markdown("</div></div>", unsafe_allow_html=True)

# About Section
st.markdown("<div id='about' style='margin: 60px 0; padding: 40px 20px;'>", unsafe_allow_html=True)
st.markdown("<div style='max-width: 1100px; margin: 0 auto;'>", unsafe_allow_html=True)

# About Header
st.markdown("""
    <div style='text-align: center; margin-bottom: 40px;'>
        <div style='display: inline-flex; align-items: center; gap: 12px; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); color: white; padding: 14px 28px; border-radius: 25px; font-weight: 700; font-size: 1.3rem; box-shadow: 0 8px 20px rgba(140, 169, 255, 0.3); animation: fadeInDown 0.6s ease;'>
            <span style='font-size: 1.5rem;'>🌿</span>
            <span>About Smart Leaf Disease Detection</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Three Info Cards
st.markdown("""
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-bottom: 40px;'>
        <div style='background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); border: 1px solid rgba(140, 169, 255, 0.3); border-radius: 20px; padding: 28px; box-shadow: 0 10px 30px rgba(140, 169, 255, 0.2); animation: fadeInLeft 0.6s ease;'>
            <div style='width: 50px; height: 50px; border-radius: 12px; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); display: grid; place-items: center; font-size: 1.8rem; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3); animation: pulse 2s ease infinite;'>🎯</div>
            <h3 style='color: var(--primary-strong); font-weight: 800; font-size: 1.2rem; margin-bottom: 12px;'>Our Mission</h3>
            <p style='color: var(--muted); line-height: 1.6; font-size: 0.95rem;'>To empower farmers, gardeners, and agricultural professionals with AI-driven tools that enable early detection and effective treatment of plant diseases, ensuring healthier crops and sustainable agriculture.</p>
        </div>
        <div style='background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); border: 1px solid rgba(140, 169, 255, 0.3); border-radius: 20px; padding: 28px; box-shadow: 0 10px 30px rgba(140, 169, 255, 0.2); animation: fadeInUp 0.7s ease;'>
            <div style='width: 50px; height: 50px; border-radius: 12px; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); display: grid; place-items: center; font-size: 1.8rem; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3); animation: pulse 2s ease infinite;'>🚀</div>
            <h3 style='color: var(--primary-strong); font-weight: 800; font-size: 1.2rem; margin-bottom: 12px;'>Technology</h3>
            <p style='color: var(--muted); line-height: 1.6; font-size: 0.95rem;'>Powered by Meta's Llama Vision models via Groq API, our system combines advanced computer vision and natural language processing to deliver accurate, real-time disease analysis with actionable treatment recommendations.</p>
        </div>
        <div style='background: linear-gradient(135deg, rgba(255, 248, 222, 0.95), rgba(255, 242, 198, 0.95)); border: 1px solid rgba(140, 169, 255, 0.3); border-radius: 20px; padding: 28px; box-shadow: 0 10px 30px rgba(140, 169, 255, 0.2); animation: fadeInRight 0.8s ease;'>
            <div style='width: 50px; height: 50px; border-radius: 12px; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); display: grid; place-items: center; font-size: 1.8rem; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3); animation: pulse 2s ease infinite;'>🔒</div>
            <h3 style='color: var(--primary-strong); font-weight: 800; font-size: 1.2rem; margin-bottom: 12px;'>Privacy & Security</h3>
            <p style='color: var(--muted); line-height: 1.6; font-size: 0.95rem;'>Your images are processed securely and are not stored on our servers. All analysis is done in real-time with complete data protection. Your privacy is our top priority.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Key Features Section
st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(140, 169, 255, 0.95), rgba(100, 140, 220, 0.95)); color: #fff; border-radius: 20px; padding: 40px; box-shadow: 0 14px 40px rgba(140, 169, 255, 0.3); margin-top: 30px; animation: fadeInUp 0.8s ease;'>
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
        <h2 style='color: #fff; font-weight: 900; font-size: 1.8rem; margin-bottom: 20px; text-align: center;'>Key Features</h2>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;'>
            <div style='display: flex; align-items: start; gap: 12px;'>
                <div style='font-size: 1.5rem;'>✅</div>
                <div><strong style='font-size: 1.05rem;'>500+ Disease Detection</strong><p style='margin: 6px 0 0; opacity: 0.9; font-size: 0.9rem;'>Comprehensive coverage of fungal, bacterial, viral, pest-related, and nutrient deficiency diseases.</p></div>
            </div>
            <div style='display: flex; align-items: start; gap: 12px;'>
                <div style='font-size: 1.5rem;'>⚡</div>
                <div><strong style='font-size: 1.05rem;'>Real-time Analysis</strong><p style='margin: 6px 0 0; opacity: 0.9; font-size: 0.9rem;'>Get results in 2-5 seconds with our optimized AI inference pipeline.</p></div>
            </div>
            <div style='display: flex; align-items: start; gap: 12px;'>
                <div style='font-size: 1.5rem;'>📊</div>
                <div><strong style='font-size: 1.05rem;'>Severity Assessment</strong><p style='margin: 6px 0 0; opacity: 0.9; font-size: 0.9rem;'>AI-powered classification of disease severity with confidence scoring.</p></div>
            </div>
            <div style='display: flex; align-items: start; gap: 12px;'>
                <div style='font-size: 1.5rem;'>💊</div>
                <div><strong style='font-size: 1.05rem;'>Treatment Recommendations</strong><p style='margin: 6px 0 0; opacity: 0.9; font-size: 0.9rem;'>Evidence-based, actionable treatment protocols tailored to specific diseases.</p></div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Built for Everyone Section
st.markdown("""
    <div style='text-align: center; margin-top: 40px; padding: 30px; background: linear-gradient(135deg, rgba(255, 248, 222, 0.9), rgba(255, 242, 198, 0.9)); border-radius: 20px; border: 1px solid rgba(140, 169, 255, 0.3); box-shadow: 0 8px 24px rgba(140, 169, 255, 0.15);'>
        <h3 style='color: var(--primary-strong); font-weight: 800; font-size: 1.3rem; margin-bottom: 16px;'>Built for Everyone</h3>
        <p style='color: var(--muted); font-size: 1rem; line-height: 1.7; max-width: 800px; margin: 0 auto;'>Whether you're a professional farmer managing large-scale operations, a home gardener tending to your backyard plants, or an agricultural researcher studying plant health, our AI-powered system provides the tools you need to protect and nurture your plants effectively.</p>
    </div>
""", unsafe_allow_html=True)

# Close containers
st.markdown("</div></div>", unsafe_allow_html=True)

# Most Common Questions Section
st.markdown("""
<style>
.faq-container {
    margin: 50px 0 !important;
    padding: 0 20px !important;
}
.faq-header-box {
    text-align: center !important;
    margin-bottom: 40px !important;
}
.faq-title-box {
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
    background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)) !important;
    color: white !important;
    padding: 14px 28px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
    box-shadow: 0 8px 20px rgba(140, 169, 255, 0.3) !important;
}
.faq-subtitle-text {
    margin-top: 20px !important;
    color: rgb(120, 140, 180) !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
.faq-grid-container {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)) !important;
    gap: 20px !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
}
.faq-card-item {
    background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(255, 248, 222, 0.95)) !important;
    border: 2px solid rgba(170, 196, 245, 0.4) !important;
    border-radius: 18px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px rgba(140, 169, 255, 0.2) !important;
}
.faq-icon-container {
    width: 50px !important;
    height: 50px !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)) !important;
    display: grid !important;
    place-items: center !important;
    font-size: 1.8rem !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3) !important;
}
.faq-question {
    color: rgb(100, 140, 220) !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    margin-bottom: 12px !important;
}
.faq-answer {
    color: rgb(120, 140, 180) !important;
    line-height: 1.7 !important;
    font-size: 0.95rem !important;
}
.faq-card-item h3 {
    color: rgb(100, 140, 220) !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    margin-bottom: 12px !important;
}
.faq-card-item p {
    color: rgb(120, 140, 180) !important;
    line-height: 1.7 !important;
    font-size: 0.95rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="faq-container"><div class="faq-header-box"><div class="faq-title-box"><span style="font-size: 1.5rem;">❓</span><span>Most Common Questions</span></div><p class="faq-subtitle-text">Quick answers to frequently asked questions</p></div><div class="faq-grid-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="faq-card-item" style="background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(255, 248, 222, 0.95)) !important; border: 2px solid rgba(170, 196, 245, 0.4) !important; border-radius: 18px !important; padding: 24px !important; box-shadow: 0 8px 24px rgba(140, 169, 255, 0.2) !important;">
        <div class="faq-icon-container" style="width: 50px !important; height: 50px !important; border-radius: 12px !important; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)) !important; display: grid !important; place-items: center !important; font-size: 1.8rem !important; margin-bottom: 16px !important; box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3) !important;">🎯</div>
        <h3 style="color: rgb(100, 140, 220) !important; font-weight: 800 !important; font-size: 1.2rem !important; margin-bottom: 12px !important;">How accurate is it?</h3>
        <p style="color: rgb(120, 140, 180) !important; line-height: 1.7 !important; font-size: 0.95rem !important;">Our AI achieves 85-95% accuracy using advanced computer vision models trained on thousands of plant disease images.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="faq-card-item" style="background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(255, 248, 222, 0.95)) !important; border: 2px solid rgba(170, 196, 245, 0.4) !important; border-radius: 18px !important; padding: 24px !important; box-shadow: 0 8px 24px rgba(140, 169, 255, 0.2) !important;">
        <div class="faq-icon-container" style="width: 50px !important; height: 50px !important; border-radius: 12px !important; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)) !important; display: grid !important; place-items: center !important; font-size: 1.8rem !important; margin-bottom: 16px !important; box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3) !important;">⚡</div>
        <h3 style="color: rgb(100, 140, 220) !important; font-weight: 800 !important; font-size: 1.2rem !important; margin-bottom: 12px !important;">How fast is it?</h3>
        <p style="color: rgb(120, 140, 180) !important; line-height: 1.7 !important; font-size: 0.95rem !important;">Analysis typically takes 2-5 seconds. Our optimized AI pipeline ensures real-time results with instant disease identification.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="faq-card-item" style="background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(255, 248, 222, 0.95)) !important; border: 2px solid rgba(170, 196, 245, 0.4) !important; border-radius: 18px !important; padding: 24px !important; box-shadow: 0 8px 24px rgba(140, 169, 255, 0.2) !important;">
        <div class="faq-icon-container" style="width: 50px !important; height: 50px !important; border-radius: 12px !important; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)) !important; display: grid !important; place-items: center !important; font-size: 1.8rem !important; margin-bottom: 16px !important; box-shadow: 0 4px 12px rgba(140, 169, 255, 0.3) !important;">🔒</div>
        <h3 style="color: rgb(100, 140, 220) !important; font-weight: 800 !important; font-size: 1.2rem !important; margin-bottom: 12px !important;">Is my data safe?</h3>
        <p style="color: rgb(120, 140, 180) !important; line-height: 1.7 !important; font-size: 0.95rem !important;">Yes! Your images are processed securely and never stored. All analysis is done in real-time with complete privacy protection.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# Professional Q&A Section with Enhanced Styling
st.markdown(
    """
    <div style="margin: 40px 0; padding: 30px; background: linear-gradient(135deg, rgba(255, 242, 198, 0.9), rgba(255, 248, 222, 0.9)); border-radius: 20px; box-shadow: 0 15px 35px rgba(140, 169, 255, 0.15); border: 2px solid rgba(170, 196, 245, 0.2);">
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="display: inline-flex; align-items: center; gap: 12px; background: linear-gradient(135deg, rgb(140, 169, 255), rgb(170, 196, 245)); color: white; padding: 12px 24px; border-radius: 25px; font-weight: 700; font-size: 1.1rem; box-shadow: 0 8px 20px rgba(140, 169, 255, 0.3);">
                <span style="font-size: 1.3rem;">❓</span>
                <span>Leaf Disease Q&A</span>
            </div>
            <p style="margin-top: 15px; color: rgb(120, 140, 180) !important; font-size: 0.95rem; font-weight: 500;">Get answers to common questions about our AI-powered disease detection system</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Professional Q&A Questions with Enhanced Styling
st.markdown(
    """
    <style>
    .qa-container { margin: 20px 0; }
    div[data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(255, 248, 222, 0.95)) !important;
        border: 2px solid rgba(170, 196, 245, 0.4) !important;
        border-radius: 18px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 8px 24px rgba(140, 169, 255, 0.2) !important;
    }
    div[data-testid="stExpander"] > div:first-child {
        background: transparent !important;
        border: none !important;
    }
    div[data-testid="stExpander"] summary {
        background: transparent !important;
        color: rgb(100, 140, 220) !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        padding: 16px 20px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: rgb(100, 140, 220) !important;
    }
    .qa-content { 
        padding: 0 20px 20px !important; 
        color: rgb(120, 140, 180) !important; 
        line-height: 1.7 !important; 
        font-size: 0.95rem !important;
    }
    .stExpander {
        background: linear-gradient(135deg, rgba(255, 242, 198, 0.95), rgba(255, 248, 222, 0.95)) !important;
        border: 2px solid rgba(170, 196, 245, 0.4) !important;
        border-radius: 18px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 8px 24px rgba(140, 169, 255, 0.2) !important;
    }
    .stExpander label {
        color: rgb(100, 140, 220) !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] p {
        color: rgb(120, 140, 180) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] {
        color: rgb(120, 140, 180) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] strong {
        color: rgb(100, 140, 220) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Q&A Questions with Professional Icons and Styling
with st.expander("🎯 How accurate is the disease detection?", expanded=False):
    st.markdown("""
    Our AI-powered system achieves **85-95% accuracy** in disease identification using advanced computer vision and machine learning models trained on thousands of plant disease images. The system continuously learns and improves its accuracy over time.
    """)

with st.expander("🔍 What types of diseases can be detected?", expanded=False):
    st.markdown(
        """
        <div class="qa-content">
            We can detect <strong>500+ plant diseases</strong> including:
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>Fungal infections (rust, powdery mildew, blight)</li>
                <li>Bacterial diseases (bacterial spot, canker)</li>
                <li>Viral infections (mosaic virus, leaf curl)</li>
                <li>Pest damage (aphids, mites, caterpillars)</li>
                <li>Nutrient deficiencies (nitrogen, phosphorus, potassium)</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("⚡ How long does analysis take?", expanded=False):
    st.markdown(
        """
        <div class="qa-content">
            Analysis typically takes <strong>2-5 seconds</strong>. The system processes your image in real-time and provides instant results with disease identification, severity assessment, and treatment recommendations. Our optimized AI models ensure fast, accurate results.
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("🔒 Is my image data secure?", expanded=False):
    st.markdown(
        """
        <div class="qa-content">
            <strong>Yes, absolutely!</strong> We prioritize privacy - your images are processed securely and are not stored on our servers. All analysis is done in real-time with complete data protection. Your privacy is our top priority.
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("📁 What image formats are supported?", expanded=False):
    st.markdown(
        """
        <div class="qa-content">
            We support <strong>JPG, JPEG, and PNG</strong> formats with a maximum file size of 200MB. For best results, use clear, well-lit images of individual leaves. Higher resolution images provide more accurate results.
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("💊 Can I get treatment recommendations?", expanded=False):
    st.markdown(
        """
        <div class="qa-content">
            <strong>Yes!</strong> Along with disease identification, we provide detailed treatment plans, prevention strategies, and step-by-step care instructions tailored to the specific disease detected. Get professional-grade recommendations instantly.
        </div>
        """,
        unsafe_allow_html=True,
    )

# Professional Footer for Q&A Section
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px; padding: 20px; background: linear-gradient(135deg, rgba(255, 248, 222, 0.3), rgba(255, 242, 198, 0.3)); border-radius: 12px; border: 2px solid rgba(170, 196, 245, 0.3); box-shadow: 0 4px 12px rgba(140, 169, 255, 0.15);">
        <p style="margin: 0; color: rgb(100, 140, 220) !important; font-size: 1rem !important; font-weight: 600 !important;">
            💡 <strong style="color: rgb(100, 140, 220) !important;">Need more help?</strong> Contact our support team or check our comprehensive documentation for advanced features.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Professional Footer
st.markdown("<div id='footer' class='footer'>", unsafe_allow_html=True)
st.markdown("<div class='footer-container'>", unsafe_allow_html=True)

# Footer Brand Section
st.markdown("""
    <div class='footer-section'>
        <div class='footer-brand'>
            <div class='logo'>🌿</div>
            <div class='name'>Smart Leaf</div>
        </div>
        <p style='color: rgb(80, 100, 140) !important; line-height: 1.8 !important; margin-bottom: 20px; font-size: 0.95rem !important; font-weight: 500 !important;'>
            AI-powered plant disease detection system helping farmers and gardeners protect their crops with advanced computer vision technology.
        </p>
        <div class='footer-social'>
            <a href='#' title='GitHub' aria-label='GitHub'>
                <svg width='20' height='20' viewBox='0 0 24 24' fill='currentColor'><path d='M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z'/></svg>
            </a>
            <a href='#' title='LinkedIn' aria-label='LinkedIn'>
                <svg width='20' height='20' viewBox='0 0 24 24' fill='currentColor'><path d='M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z'/></svg>
            </a>
            <a href='#' title='Twitter' aria-label='Twitter'>
                <svg width='20' height='20' viewBox='0 0 24 24' fill='currentColor'><path d='M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z'/></svg>
            </a>
            <a href='#' title='Email' aria-label='Email'>
                <svg width='20' height='20' viewBox='0 0 24 24' fill='currentColor'><path d='M12 12.713l-11.985-9.713h23.97l-11.985 9.713zm0 2.574l-12-9.725v15.438h24v-15.438l-12 9.725z'/></svg>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Footer Quick Links
st.markdown("""
    <div class='footer-section'>
        <h3>Quick Links</h3>
        <a href='#detect-desc'>Disease Detection</a>
        <a href='#features-desc'>Features</a>
        <a href='#about'>About Us</a>
        <a href='#footer'>Contact</a>
    </div>
""", unsafe_allow_html=True)

# Footer Resources
st.markdown("""
    <div class='footer-section'>
        <h3>Resources</h3>
        <a href='#'>Documentation</a>
        <a href='#'>API Reference</a>
        <a href='#'>Tutorials</a>
        <a href='#'>Support Center</a>
    </div>
""", unsafe_allow_html=True)

# Footer Technology
st.markdown("""
    <div class='footer-section'>
        <h3>Technology</h3>
        <p style='color: rgb(80, 100, 140) !important; line-height: 1.8 !important; margin-bottom: 15px; font-size: 0.95rem !important; font-weight: 500 !important;'>
            Powered by Meta Llama Vision models via Groq API. Built with Streamlit and FastAPI for real-time disease analysis.
        </p>
        <div style='display: flex; gap: 8px; flex-wrap: wrap; margin-top: 15px;'>
            <span style='background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.15);'>AI-Powered</span>
            <span style='background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.15);'>Real-time</span>
            <span style='background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.15);'>Secure</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Close footer container
st.markdown("</div>", unsafe_allow_html=True)

# Footer Bottom
st.markdown("""
    <div class='footer-bottom'>
        <div class='copyright'>
            © 2024 Smart Leaf Disease Detection. All rights reserved.
        </div>
        <div class='links'>
            <a href='#'>Privacy Policy</a>
            <a href='#'>Terms of Service</a>
            <a href='#'>Cookie Policy</a>
            <a href='#'>License</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Close footer
st.markdown("</div>", unsafe_allow_html=True)

# Chatbot Component
st.markdown("""
    <input type="checkbox" id="chatbot-toggle" class="chatbot-toggle" style="display: none;">
    <label for="chatbot-toggle" class="floating-action" title="Ask Questions"></label>
    <div class="chatbot-modal" id="chatbot-modal">
        <div class="chatbot-header">
            <div class="icon">💬</div>
            <div>AI Assistant</div>
            <label for="chatbot-toggle" style="margin-left: auto; cursor: pointer; font-size: 1.2rem;">✕</label>
        </div>
        <div class="chatbot-content">
            <div class="chatbot-question">
                <input type="checkbox" id="q1" style="display: none;">
                <label for="q1">How accurate is the disease detection?</label>
                <div class="chatbot-answer">
                    Our AI-powered system achieves 85-95% accuracy in disease identification using advanced computer vision models trained on thousands of plant disease images.
                </div>
            </div>
            <div class="chatbot-question">
                <input type="checkbox" id="q2" style="display: none;">
                <label for="q2">What types of diseases can be detected?</label>
                <div class="chatbot-answer">
                    We can detect 500+ plant diseases including fungal infections, bacterial diseases, viral infections, pest damage, and nutrient deficiencies.
                </div>
            </div>
            <div class="chatbot-question">
                <input type="checkbox" id="q3" style="display: none;">
                <label for="q3">How long does analysis take?</label>
                <div class="chatbot-answer">
                    Analysis typically takes 2-5 seconds. The system processes your image in real-time and provides instant results with disease identification and treatment recommendations.
                </div>
            </div>
            <div class="chatbot-question">
                <input type="checkbox" id="q4" style="display: none;">
                <label for="q4">Is my image data secure?</label>
                <div class="chatbot-answer">
                    Yes! Your images are processed securely and are not stored on our servers. All analysis is done in real-time with complete data protection.
                </div>
            </div>
            <div class="chatbot-question">
                <input type="checkbox" id="q5" style="display: none;">
                <label for="q5">What image formats are supported?</label>
                <div class="chatbot-answer">
                    We support JPG, JPEG, and PNG formats with a maximum file size of 200MB. For best results, use clear, well-lit images of individual leaves.
                </div>
            </div>
            <div class="chatbot-question">
                <input type="checkbox" id="q6" style="display: none;">
                <label for="q6">Can I get treatment recommendations?</label>
                <div class="chatbot-answer">
                    Yes! Along with disease identification, we provide detailed treatment plans, prevention strategies, and step-by-step care instructions tailored to the specific disease detected.
                </div>
            </div>
        </div>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const chatbotToggle = document.getElementById('chatbot-toggle');
        const chatbotModal = document.getElementById('chatbot-modal');
        const floatingAction = document.querySelector('.floating-action');
        
        if (floatingAction) {
            floatingAction.addEventListener('click', function(e) {
                e.preventDefault();
                if (chatbotToggle) {
                    chatbotToggle.checked = !chatbotToggle.checked;
                    if (chatbotToggle.checked) {
                        chatbotModal.classList.add('show');
                    } else {
                        chatbotModal.classList.remove('show');
                    }
                }
            });
        }
        
        // Close on outside click
        document.addEventListener('click', function(e) {
            if (chatbotModal && chatbotToggle && chatbotToggle.checked) {
                if (!chatbotModal.contains(e.target) && !floatingAction.contains(e.target)) {
                    chatbotToggle.checked = false;
                    chatbotModal.classList.remove('show');
                }
            }
        });
    });
    </script>
""", unsafe_allow_html=True)
