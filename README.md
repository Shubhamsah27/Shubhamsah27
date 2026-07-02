<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DripCheck — Rate the Drip</title>
    <!-- Google Fonts: Space Grotesk, Inter, DM Mono -->
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body>
    <!-- Background visual layout elements -->
    <div class="bg-blur bg-blur-1"></div>
    <div class="bg-blur bg-blur-2"></div>
    <div class="noise-overlay"></div>

    <!-- App Wrapper (Fully Responsive) -->
    <div class="app-wrapper" id="app-wrapper">
        <!-- App Content Viewport -->
        <div class="phone-viewport">
                <!-- App Header -->
                <header class="app-header">
                    <div class="header-logo">
                        <span class="logo-sparkle">✦</span>
                        <span class="logo-text">DripCheck</span>
                    </div>
                    <div class="header-actions">
                        <button class="header-btn" id="api-key-indicator" title="Configure Gemini API Key">
                            <i data-lucide="key"></i>
                        </button>
                        <button class="header-btn notification-btn">
                            <i data-lucide="bell"></i>
                            <span class="notification-badge">3</span>
                        </button>
                    </div>
                </header>

                <!-- Page Container -->
                <main class="page-content" id="page-content">
                    
                    <!-- 1. FEED / HOME SCREEN -->
                    <section class="page active" id="page-landing">
                        <!-- Welcome Banner (Light card on dark contrast) -->
                        <div class="welcome-banner">
                            <div class="welcome-text">
                                <span class="welcome-title">Hey cutie! 🧡</span>
                                <span class="welcome-sub">Your daily drip awaits ✨</span>
                            </div>
                        </div>

                        <!-- Live Stats Ticker -->
                        <div class="live-ticker">
                            <div class="ticker-content">
                                <span>🔥 Top Score: 98</span>
                                <span class="ticker-dot">•</span>
                                <span>⚡ 12,483 fits rated today</span>
                                <span class="ticker-dot">•</span>
                                <span>👟 Streetwear trending</span>
                            </div>
                        </div>

                        <!-- Community Feed Posts -->
                        <div class="featured-preview">
                            <div class="feed-list" id="feed-list">
                                <!-- Populated dynamically by JS -->
                            </div>
                        </div>
                        
                        <div class="end-of-feed">You're all caught up 🎯 ✨</div>
                    </section>

                    <!-- 2. RATE/SWIPE SCREEN -->
                    <section class="page" id="page-rate">
                        <!-- Card Stack Deck -->
                        <div class="card-stack-container">
                            <div class="card-deck" id="card-deck">
                                <!-- Populated dynamically by JS -->
                            </div>
                            
                            <!-- No more cards state -->
                            <div class="no-cards-state" id="no-cards-state" style="display: none;">
                                <div class="empty-icon">🎉</div>
                                <h3>You're all caught up!</h3>
                                <p>Come back later or upload your fit to keep the game going.</p>
                                <button class="btn btn-primary btn-sm nav-trigger" data-target="upload" style="margin: 15px auto 0;">
                                    Upload My Fit
                                </button>
                            </div>
                        </div>

                        <!-- Stack card indicator labels overlay (green/red) -->
                        <div class="swipe-overlay-badges">
                            <span class="swipe-badge swipe-badge-pass" id="badge-swipe-pass">💀 PASS</span>
                            <span class="swipe-badge swipe-badge-fire" id="badge-swipe-fire">🔥 FIRE</span>
                        </div>

                        <!-- Sub-card Info Overlay -->
                        <div class="rate-card-details-box" id="rate-card-details-box">
                            <div class="details-top">
                                <h3 id="rate-username">@minimalist_bae</h3>
                                <span class="score-pill-drip" id="rate-avg-score">⭐ 92%</span>
                            </div>
                            <div class="details-tags" id="rate-tags">
                                <span class="card-tag">#streetwear</span>
                            </div>
                        </div>

                        <!-- Action Controls -->
                        <div class="rate-actions-row">
                            <button class="action-btn btn-undo" id="btn-undo" title="Undo Last Vote" disabled>
                                <i data-lucide="rotate-ccw"></i>
                            </button>
                            <button class="circle-action-btn btn-pass" id="btn-swipe-pass" title="Pass (Swipe Left)">
                                ✕
                            </button>
                            <button class="circle-action-btn btn-fire" id="btn-swipe-fire" title="Fire (Swipe Right)">
                                ❤️
                            </button>
                        </div>
                    </section>

                    <!-- 3. AI RATING RESULT SCREEN -->
                    <section class="page" id="page-result">
                        <div class="result-header">
                            <h2 class="page-title">AI Style Report</h2>
                            <p class="page-subtitle" id="result-caption">"Casual streetwear setup"</p>
                        </div>

                        <!-- Score Reveal Hero Ring -->
                        <div class="result-score-reveal">
                            <div class="score-glow-emitter" id="score-glow-emitter"></div>
                            <div class="svg-ring-container">
                                <svg viewBox="0 0 120 120">
                                    <defs>
                                        <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                            <stop offset="0%" stop-color="#a855f7" />
                                            <stop offset="50%" stop-color="#ec4899" />
                                            <stop offset="100%" stop-color="#f97316" />
                                        </linearGradient>
                                    </defs>
                                    <circle class="ring-bg" cx="60" cy="60" r="50"></circle>
                                    <!-- Tick marks -->
                                    <circle class="ring-ticks" cx="60" cy="60" r="50" stroke-dasharray="2 6"></circle>
                                    <circle class="ring-fill" id="ring-score-fill" cx="60" cy="60" r="50"></circle>
                                </svg>
                                <div class="ring-inner-text">
                                    <div class="score-value-digit" id="score-value-digit">0</div>
                                    <div class="score-grade-text gradient-text" id="score-grade-text">S TIER</div>
                                </div>
                            </div>
                        </div>

                        <!-- Detailed Stylist Report -->
                        <div class="stylist-report-container">
                            
                            <!-- ⭐ Overall Review -->
                            <div class="stylist-section section-overall">
                                <h3 class="stylist-section-title"><span class="sparkle-icon">⭐</span> Overall Review</h3>
                                <p class="stylist-text" id="report-overall-review">Generating analysis...</p>
                            </div>

                            <!-- ✅ What Looks Good & 🔧 Improvements -->
                            <div class="stylist-grid-2">
                                <div class="stylist-section box-strengths">
                                    <h4 class="stylist-section-title"><span class="sparkle-icon">✅</span> What Works</h4>
                                    <ul class="stylist-list" id="report-strengths"></ul>
                                </div>
                                <div class="stylist-section box-weaknesses">
                                    <h4 class="stylist-section-title"><span class="sparkle-icon">🔧</span> Needs Work</h4>
                                    <ul class="stylist-list" id="report-weaknesses"></ul>
                                </div>
                            </div>

                            <!-- 👕 Clothing Suggestions -->
                            <div class="stylist-accordion">
                                <button class="accordion-trigger">
                                    <span class="accordion-title"><span class="sparkle-icon">👕</span> Clothing Suggestions</span>
                                    <i data-lucide="chevron-down" class="accordion-icon"></i>
                                </button>
                                <div class="accordion-content">
                                    <ul class="stylist-list" id="report-clothing"></ul>
                                </div>
                            </div>

                            <!-- 👟 Footwear & ⌚ Accessories -->
                            <div class="stylist-accordion">
                                <button class="accordion-trigger">
                                    <span class="accordion-title"><span class="sparkle-icon">👟</span> Footwear & Accessories</span>
                                    <i data-lucide="chevron-down" class="accordion-icon"></i>
                                </button>
                                <div class="accordion-content">
                                    <div class="split-lists">
                                        <div>
                                            <h5>Footwear</h5>
                                            <ul class="stylist-list" id="report-footwear"></ul>
                                        </div>
                                        <div style="margin-top: 10px;">
                                            <h5>Accessories</h5>
                                            <ul class="stylist-list" id="report-accessories"></ul>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 🎨 Color Palette -->
                            <div class="stylist-accordion">
                                <button class="accordion-trigger">
                                    <span class="accordion-title"><span class="sparkle-icon">🎨</span> Recommended Colors</span>
                                    <i data-lucide="chevron-down" class="accordion-icon"></i>
                                </button>
                                <div class="accordion-content">
                                    <div class="color-palette-container" id="report-colors">
                                        <!-- Populated via JS -->
                                    </div>
                                </div>
                            </div>

                            <!-- 📍 Best Occasions -->
                            <div class="stylist-accordion">
                                <button class="accordion-trigger">
                                    <span class="accordion-title"><span class="sparkle-icon">📍</span> Occasion Suitability</span>
                                    <i data-lucide="chevron-down" class="accordion-icon"></i>
                                </button>
                                <div class="accordion-content">
                                    <div class="occasions-list" id="report-occasions">
                                        <!-- Populated via JS -->
                                    </div>
                                </div>
                            </div>

                            <!-- 💡 Style Tips -->
                            <div class="stylist-accordion">
                                <button class="accordion-trigger">
                                    <span class="accordion-title"><span class="sparkle-icon">💡</span> Personalized Style Tips</span>
                                    <i data-lucide="chevron-down" class="accordion-icon"></i>
                                </button>
                                <div class="accordion-content">
                                    <ul class="stylist-list" id="report-tips"></ul>
                                </div>
                            </div>

                        </div>

                        <!-- Actions -->
                        <div class="result-actions-stack">
                            <button class="btn btn-primary btn-glow w-100" id="btn-share-report">
                                <i data-lucide="share-2"></i>
                                <span>Share Result</span>
                            </button>
                            <button class="btn btn-secondary w-100" id="btn-post-community">
                                <i data-lucide="users"></i>
                                <span>Post to Community</span>
                            </button>
                            <button class="btn btn-dark w-100 nav-trigger" data-target="upload">
                                <i data-lucide="refresh-cw"></i>
                                <span>Try Another Fit</span>
                            </button>
                        </div>
                    </section>

                    <!-- 4. LEADERBOARD SCREEN -->
                    <section class="page" id="page-leaderboard">
                        <div class="leaderboard-heading-box">
                            <div class="header-card-white">
                                <span class="crown-icon">👑</span>
                                <h2 class="page-title">Top Drippers</h2>
                                <p class="page-subtitle">This week's most iconic fits</p>
                            </div>
                        </div>

                        <!-- Segmented Switch Tab Filters -->
                        <div class="segmented-control">
                            <button class="seg-tab active" data-time="today">Today</button>
                            <button class="seg-tab" data-time="week">This Week</button>
                            <button class="seg-tab" data-time="all">All-Time</button>
                        </div>

                        <!-- Podium (Top 3 Cards) -->
                        <div class="podium-row">
                            <!-- #2 Podium -->
                            <div class="podium-col podium-col-2" id="podium-2">
                                <div class="podium-avatar-wrapper">
                                    <img class="podium-avatar" src="" alt="avatar">
                                    <span class="podium-rank-num rank-num-2">2</span>
                                </div>
                                <div class="podium-username">@user</div>
                                <span class="podium-score">0%</span>
                            </div>

                            <!-- #1 Podium -->
                            <div class="podium-col podium-col-1" id="podium-1">
                                <div class="podium-avatar-wrapper">
                                    <div class="crown-overlay">👑</div>
                                    <img class="podium-avatar" src="" alt="avatar">
                                    <span class="podium-rank-num rank-num-1">1</span>
                                </div>
                                <div class="podium-username">@user</div>
                                <span class="podium-score">0%</span>
                            </div>

                            <!-- #3 Podium -->
                            <div class="podium-col podium-col-3" id="podium-3">
                                <div class="podium-avatar-wrapper">
                                    <img class="podium-avatar" src="" alt="avatar">
                                    <span class="podium-rank-num rank-num-3">3</span>
                                </div>
                                <div class="podium-username">@user</div>
                                <span class="podium-score">0%</span>
                            </div>
                        </div>

                        <!-- Scrollable list of ranks -->
                        <div class="ranks-list" id="ranks-list">
                            <!-- Populated dynamically by JS -->
                        </div>

                        <!-- Live Challenges Section -->
                        <div class="challenges-section">
                            <h3 class="section-title">🔥 Live Challenges</h3>
                            <div class="challenges-grid" id="challenges-grid">
                                <!-- Populated dynamically by JS -->
                            </div>
                        </div>
                    </section>

                    <!-- 5. PROFILE SCREEN -->
                    <section class="page" id="page-profile">
                        <!-- Profile Card -->
                        <div class="profile-card">
                            <span class="profile-abs-decor decor-left">🌸</span>
                            <span class="profile-abs-decor decor-right">✦</span>
                            
                            <div class="profile-header-meta">
                                <div class="profile-avatar-holder">
                                    <img src="" alt="avatar" id="my-profile-avatar">
                                    <button class="btn-avatar-upload" id="btn-upload-avatar">
                                        <i data-lucide="camera" style="width: 12px; height: 12px;"></i>
                                    </button>
                                </div>
                                <h3 id="my-profile-username">@username</h3>
                                <p id="my-profile-bio">Style enthusiast...</p>
                                <span class="weekly-rank-pill">🏅 Rank #2 this week</span>
                            </div>
                        </div>

                        <!-- Stats Row Bubbles -->
                        <div class="profile-bubbles-row">
                            <div class="stat-bubble bubble-pink">
                                <span class="bubble-num" id="profile-likes-count">1,240</span>
                                <span class="bubble-label">LIKES</span>
                            </div>
                            <div class="stat-bubble bubble-yellow">
                                <span class="bubble-num" id="profile-posts-count">1</span>
                                <span class="bubble-label">POSTS</span>
                            </div>
                            <div class="stat-bubble bubble-teal">
                                <span class="bubble-num" id="profile-avg-drip">98%</span>
                                <span class="bubble-label">AVG DRIP</span>
                            </div>
                        </div>

                        <!-- Badges Section -->
                        <div class="badges-card">
                            <h4>🎖 Your Badges</h4>
                            <div class="badges-wrap">
                                <span class="badge-pill">🔥 On Fire</span>
                                <span class="badge-pill">💎 Top 10</span>
                                <span class="badge-pill">🌸 Soft Girl</span>
                                <span class="badge-pill">👟 Sneakerhead</span>
                                <span class="badge-pill">🎨 Style Icon</span>
                            </div>
                        </div>

                        <!-- My Drips Section -->
                        <div class="profile-grid-section">
                            <h4 class="section-title">📌 My Drips</h4>
                            <div class="drips-grid" id="profile-drips-grid">
                                <!-- Grid items populated dynamically -->
                            </div>
                        </div>

                        <!-- Saved Style Advice -->
                        <div class="advice-card">
                            <p class="advice-placeholder">Scan a fit and save the AI's tips to keep them here ✨</p>
                        </div>

                        <!-- Settings Trigger -->
                        <button class="btn btn-dark w-100" id="btn-settings-trigger">
                            <i data-lucide="settings"></i>
                            <span>Settings / API Key</span>
                        </button>
                    </section>

                </main>

                <!-- Page Load scanning animation overlay -->
                <div class="scan-loading-overlay" id="scan-loading-overlay" style="display: none;">
                    <div class="scan-box">
                        <div class="scan-image-box">
                            <img src="" id="scan-image-preview" alt="scanning fit">
                            <div class="scan-laser-line"></div>
                        </div>
                        <div class="scan-status-group">
                            <div class="spinner"></div>
                            <h3>Analyzing your drip...</h3>
                            <p>The AI critic is grading color coordination 🎨</p>
                        </div>
                    </div>
                </div>

                <!-- Bottom sheet upload modal (Slides up, blurred background overlay) -->
                <div class="sheet-modal" id="upload-sheet">
                    <div class="sheet-overlay" id="btn-close-upload-overlay"></div>
                    <div class="sheet-content">
                        <div class="sheet-drag-handle"></div>
                        <button class="sheet-close-btn" id="btn-close-upload-x">✕</button>
                        
                        <div class="sheet-body">
                            <h3 class="sheet-title">Drop your fit 📸</h3>
                            <p class="sheet-subtitle">Upload today's look and the AI stylist will scan it for tips.</p>
                            
                            <!-- Drop upload zone -->
                            <div class="dashed-upload-zone" id="upload-drop-zone">
                                <input type="file" id="upload-file-input" accept="image/*" style="display: none;">
                                <div class="upload-zone-prompt" id="upload-zone-prompt">
                                    <div class="prompt-camera-icon">📷</div>
                                    <p class="prompt-main">Tap to upload</p>
                                </div>
                                <div class="upload-zone-preview" id="upload-zone-preview" style="display: none;">
                                    <img src="" id="upload-preview-img" alt="fit">
                                    <button class="remove-preview-btn" id="btn-remove-preview">✕</button>
                                </div>
                            </div>

                            <div class="input-group">
                                <label for="sheet-fit-caption">Caption</label>
                                <input type="text" id="sheet-fit-caption" placeholder="E.g. Vintage leather coat vibes...">
                            </div>

                            <div class="input-group">
                                <label for="sheet-fit-tags">Tags (e.g. streetwear, y2k)</label>
                                <input type="text" id="sheet-fit-tags" placeholder="streetwear, casual">
                            </div>

                            <button class="btn btn-primary btn-glow w-100" id="btn-submit-fit" style="height: 56px; border-radius: 100px;">
                                Scan my drip ✨
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Settings Drawer -->
                <div class="sheet-modal" id="settings-sheet">
                    <div class="sheet-overlay" id="btn-close-settings-overlay"></div>
                    <div class="sheet-content">
                        <div class="sheet-drag-handle"></div>
                        <button class="sheet-close-btn" id="btn-close-settings-x">✕</button>
                        
                        <div class="sheet-body">
                            <h3 class="sheet-title">DripCheck Settings ⚙️</h3>
                            <p class="sheet-subtitle">Configure your custom Gemini API settings</p>
                            
                            <div class="input-group">
                                <label for="settings-api-key">Gemini API Key</label>
                                <input type="password" id="settings-api-key" placeholder="AIzaSy...">
                            </div>
                            
                            <a href="https://aistudio.google.com/" target="_blank" class="api-key-link" style="margin-bottom: 20px; display: block;">
                                <i data-lucide="external-link" style="width: 12px; height: 12px;"></i> Get a Free Gemini API Key
                            </a>

                            <div class="drawer-actions">
                                <button class="btn btn-primary w-100" id="btn-save-settings">Save API Key</button>
                                <button class="btn btn-dark w-100" id="btn-use-mock-mode">Use Local Demo Mode</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Comments Sheet -->
                <div class="sheet-modal" id="comments-sheet">
                    <div class="sheet-overlay" id="btn-close-comments-overlay"></div>
                    <div class="sheet-content">
                        <div class="sheet-drag-handle"></div>
                        <button class="sheet-close-btn" id="btn-close-comments-x">✕</button>
                        
                        <div class="sheet-body" style="display: flex; flex-direction: column; height: 100%;">
                            <h3 class="sheet-title" style="margin-bottom: 10px;">Comments</h3>
                            <div class="comments-list" id="comments-list" style="flex: 1; overflow-y: auto; margin-bottom: 15px;">
                                <!-- Comments populated by JS -->
                            </div>
                            <div class="comment-input-area">
                                <input type="text" id="new-comment-text" placeholder="Add a comment...">
                                <button class="btn btn-primary btn-sm" id="btn-submit-comment">Post</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Toast Notifications -->
                <div class="toast-notification" id="toast-notification">
                    <span id="toast-message">Result copied!</span>
                </div>

                <!-- Fixed Bottom Navigation Bar -->
                <nav class="app-nav">
                    <button class="nav-btn active" data-page="landing" title="Home">
                        <i data-lucide="home"></i>
                        <span>Home</span>
                    </button>
                    <button class="nav-btn" data-page="rate" title="Rate Fits">
                        <i data-lucide="sparkles"></i>
                        <span>Rate</span>
                    </button>
                    <button class="nav-btn btn-nav-upload" id="btn-trigger-upload-sheet" title="Upload Fit">
                        <div class="nav-upload-circle">
                            <i data-lucide="camera"></i>
                        </div>
                    </button>
                    <button class="nav-btn" data-page="leaderboard" title="Leaderboard">
                        <i data-lucide="crown"></i>
                        <span>Leaders</span>
                    </button>
                    <button class="nav-btn" data-page="profile" title="Profile">
                        <i data-lucide="user"></i>
                        <span>Profile</span>
                    </button>
                </nav>

            </div>
        </div>

    <!-- Custom Cursor -->
    <div class="custom-cursor-flower">🌸</div>
    <div class="custom-cursor-dot"></div>

    <!-- Main JavaScript Logic -->
    <script src="app.js"></script>
</body>
</html>
