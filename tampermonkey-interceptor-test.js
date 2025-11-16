// ==UserScript==
// @name         API Interceptor Test
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Simple API interceptor that shows matched data
// @match        *://myprize.us/*
// @grant        none
// @run-at       document-start
// ==/UserScript==
//
// To add more sites, add more @match lines above:
// @match        *://othersite.com/*
// @match        *://anothersite.com/*

(function() {
    'use strict';

    //----------------------------------------------------
    // SITE ADAPTERS
    //----------------------------------------------------
    
    const ADAPTERS = {
        'myprize.us': {
            name: 'MyPrize',
            enabled: true,
            apiPatterns: [
                /\/api\/player\/games\/slug\//
            ],
            parseResponse: (data) => {
                return {
                    name: data.name,
                    provider: data.studio
                };
            }
        }
        
        // Add more site adapters here:
        // 'othersite.com': {
        //     name: 'Other Site',
        //     enabled: true,
        //     apiPatterns: [/\/api\/game\//],
        //     parseResponse: (data) => ({
        //         name: data.title,
        //         provider: data.vendor
        //     })
        // }
    };

    //----------------------------------------------------
    // INTERCEPTION
    //----------------------------------------------------
    
    // Check if this site has an adapter
    const hostname = window.location.hostname;
    const adapter = ADAPTERS[hostname];
    
    if (!adapter || !adapter.enabled) {
        console.log('[Interceptor] No adapter for:', hostname);
        return; // Exit early
    }
    
    console.log(`[Interceptor] Script loaded for ${adapter.name}`);
    
    //----------------------------------------------------
    // CSV DATA
    //----------------------------------------------------
    
    const CSV_URL = 'https://rtp-data.pages.dev/rtp_data.csv';
    let rtpData = [];
    
    async function loadCSV() {
        try {
            console.log('[Interceptor] Loading CSV from:', CSV_URL);
            const response = await fetch(CSV_URL);
            const text = await response.text();
            rtpData = parseCSV(text);
            console.log('[Interceptor] CSV loaded:', rtpData.length, 'games');
            
            // Show confirmation popup
            showLoadedPopup(rtpData.length);
        } catch (error) {
            console.error('[Interceptor] Failed to load CSV:', error);
        }
    }
    
    function parseCSV(text) {
        const lines = text.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            if (values.length >= 4) {
                const entry = {};
                headers.forEach((header, index) => {
                    entry[header] = values[index] ? values[index].trim() : '';
                });
                data.push(entry);
            }
        }
        
        return data;
    }
    
    function showLoadedPopup(count) {
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a1a;
            color: #fff;
            border: 2px solid #4ade80;
            border-radius: 12px;
            padding: 24px 32px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            z-index: 9999999;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8);
            text-align: center;
        `;
        
        popup.innerHTML = `
            <div style="font-size: 48px; color: #4ade80; margin-bottom: 16px;">✓</div>
            <div style="font-weight: bold; font-size: 18px; margin-bottom: 8px;">CSV Data Loaded</div>
            <div style="color: #888; font-size: 14px;">${count} games in database</div>
        `;
        
        document.body.appendChild(popup);
        
        // Remove popup after 3 seconds
        setTimeout(() => {
            popup.remove();
        }, 3000);
    }
    
    function normalizeString(str) {
        if (!str) return '';
        return str.toLowerCase().trim().replace(/[^a-z0-9]/g, '');
    }
    
    function lookupRTP(gameInfo) {
        if (!gameInfo || rtpData.length === 0) return null;
        
        const normalizedGameName = normalizeString(gameInfo.name);
        const normalizedProvider = normalizeString(gameInfo.provider);
        
        console.log('[Interceptor] Looking for game:', gameInfo.name);
        console.log('[Interceptor] Normalized:', normalizedGameName);
        console.log('[Interceptor] Provider:', normalizedProvider);
        
        // Search for matching game
        const match = rtpData.find(entry => {
            const entryGame = normalizeString(entry.game);
            const entryPublisher = normalizeString(entry.publisher);
            
            // Match game name and provider/studio
            const gameMatch = entryGame === normalizedGameName;
            const providerMatch = entryPublisher === normalizedProvider;
            
            return gameMatch && providerMatch;
        });
        
        if (match) {
            console.log('[Interceptor] RTP Match found:', match);
        } else {
            console.log('[Interceptor] No RTP match found');
        }
        
        return match;
    }
    
    //----------------------------------------------------
    // WIDGET STATE
    //----------------------------------------------------
    
    let widget = null;
    let currentGameInfo = null;
    
    // Create widget when game data is detected
    function createWidget() {
        if (widget) return; // Already exists
        
        widget = document.createElement('div');
        widget.id = 'interceptor-widget';
        widget.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1a1a1a;
            color: #fff;
            border: 2px solid #444;
            border-radius: 12px;
            padding: 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            z-index: 999999;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8);
            min-width: 350px;
        `;
        
        document.body.appendChild(widget);
    }
    
    function updateWidget(rtpMatch) {
        if (!widget || !currentGameInfo) return;
        
        if (!rtpMatch) {
            widget.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <div style="font-size: 18px; font-weight: bold; color: #fff; margin-bottom: 8px;">
                        ${currentGameInfo.name}
                    </div>
                    <div style="color: #888; font-size: 12px; margin-bottom: 20px;">
                        (${currentGameInfo.provider})
                    </div>
                    <div style="color: #ff6b6b; font-size: 14px;">⚠ No RTP data found</div>
                </div>
            `;
            return;
        }
        
        // Get verified RTP if available for this site
        const siteName = hostname.split('.')[0]; // e.g., "myprize" from "myprize.us"
        const verifiedRTP = rtpMatch[siteName];
        const hasVerified = verifiedRTP && verifiedRTP.trim() !== '';
        
        widget.innerHTML = `
            <div style="text-align: center; margin-bottom: 16px;">
                <div style="font-size: 18px; font-weight: bold; color: #fff; margin-bottom: 4px;">
                    ${rtpMatch.game}
                </div>
                <div style="color: #888; font-size: 12px;">
                    (${rtpMatch.publisher})
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px;">
                <div style="background: #2a2a2a; border: 1px solid #444; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Min</div>
                    <div style="color: #4ade80; font-size: 18px; font-weight: bold;">${rtpMatch.min_rtp}%</div>
                </div>
                <div style="background: #2a2a2a; border: 1px solid #444; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Max</div>
                    <div style="color: #4ade80; font-size: 18px; font-weight: bold;">${rtpMatch.max_rtp}%</div>
                </div>
                <div style="background: ${hasVerified ? '#2a3a2a' : '#3a2a2a'}; border: 1px solid ${hasVerified ? '#4ade80' : '#ff6b6b'}; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Verified</div>
                    <div style="color: ${hasVerified ? '#4ade80' : '#ff6b6b'}; font-size: ${hasVerified ? '18px' : '11px'}; font-weight: bold;">
                        ${hasVerified ? verifiedRTP + '%' : 'UNVERIFIED'}
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #333;">
                <div style="color: #888; font-size: 10px; margin-bottom: 4px;">Raw Data:</div>
                <pre style="margin: 0; font-size: 10px; max-height: 200px; overflow: auto; background: #000; padding: 8px; border-radius: 4px; font-family: monospace;">${JSON.stringify(currentGameInfo, null, 2)}</pre>
            </div>
        `;
    }
    
    // Widget will be created when game data is detected (no initial widget)
    
    // Intercept fetch
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const url = args[0] instanceof Request ? args[0].url : args[0];
        const response = await originalFetch.apply(this, args);
        
        // Check if this URL matches adapter patterns
        const matches = adapter.apiPatterns.some(pattern => pattern.test(url));
        
        if (matches) {
            console.log('[Interceptor] ✓ MATCHED:', url);
            
            // Clone and parse response
            const clonedResponse = response.clone();
            try {
                const text = await clonedResponse.text();
                const data = JSON.parse(text);
                console.log('[Interceptor] Response data:', data);
                
                const parsed = adapter.parseResponse(data);
                console.log('[Interceptor] Parsed game info:', parsed);
                
                // Look up RTP data
                const rtpMatch = lookupRTP(parsed);
                
                // Update widget with game info and RTP data
                currentGameInfo = parsed;
                createWidget(); // Create widget if needed
                updateWidget(rtpMatch);
            } catch (e) {
                console.error('[Interceptor] Parse error:', e);
            }
        }
        
        return response;
    };
    
    console.log('[Interceptor] Ready');
    
    // Load CSV data
    loadCSV();

})();
