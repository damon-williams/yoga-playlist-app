// Disable PostHog temporarily
window.posthog = {
    capture: function() {
        console.log('PostHog disabled - would have tracked:', arguments);
    }
};

// Configuration
const API_BASE_URL = '/api';

// DOM Elements
const backendStatus = document.getElementById('backend-status');
const spotifyStatus = document.getElementById('spotify-status');
const classTypeSelect = document.getElementById('class-type');
const musicPreferences = document.getElementById('music-preferences');
const durationSlider = document.getElementById('duration');
const durationDisplay = document.getElementById('duration-display');
const playlistForm = document.getElementById('playlist-form');
const generateBtn = document.getElementById('generate-btn');
const outputContent = document.getElementById('output-content');
const exportSection = document.getElementById('export-section');
const playlistNameInput = document.getElementById('playlist-name');
const exportBtn = document.getElementById('export-btn');
const exportResult = document.getElementById('export-result');

// Global state
let currentPlaylistData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Yoga Playlist Generator starting...');
    
    // Track app start
    if (typeof posthog !== 'undefined') {
        posthog.capture('app_loaded', {
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent
        });
    }

    // Setup event listeners
    setupEventListeners();
    
    // Check system status
    checkSystemStatus();
    
    // Load available classes
    loadYogaClasses();

    // Check if user is returning from Spotify authorization
    const authCode = getSpotifyAuthCodeFromURL();
    const pendingPlaylist = localStorage.getItem('pendingPlaylist');
    
    if (authCode && pendingPlaylist) {
        // User has returned from Spotify - auto-create the playlist
        setTimeout(() => {
            const playlistData = JSON.parse(pendingPlaylist);
            createPlaylistWithAuthCode(playlistData.playlistName, playlistData.trackIds, authCode);
        }, 1000); // Small delay to ensure page is fully loaded
    }
});

function setupEventListeners() {
    // Duration slider
    durationSlider.addEventListener('input', function() {
        durationDisplay.textContent = this.value;
    });
    
    // Form submission
    playlistForm.addEventListener('submit', handlePlaylistGeneration);
    
    // Export button
    exportBtn.addEventListener('click', handleSpotifyExport);
    
    // Class type selection (new)
    classTypeSelect.addEventListener('change', handleClassTypeChange);
}

function handleClassTypeChange() {
    if (classTypeSelect.value === '__ADD_NEW__') {
        showAddNewClassInterface();
    }
}

function showAddNewClassInterface() {
    // Replace the select with input fields
    const formGroup = classTypeSelect.closest('.form-group');
    
    formGroup.innerHTML = `
        <label for="new-class-name">New Class Name</label>
        <input type="text" id="new-class-name" placeholder="e.g., Hot Power Flow" required>
        
        <label for="new-class-description">Class Description</label>
        <textarea id="new-class-description" placeholder="Describe the style, intensity, and focus of this class..." required></textarea>
        
        <div class="add-class-actions">
            <button type="button" id="save-new-class" class="save-class-btn">Save & Use This Class</button>
            <button type="button" id="cancel-new-class" class="cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners for new buttons
    document.getElementById('save-new-class').addEventListener('click', saveNewClass);
    document.getElementById('cancel-new-class').addEventListener('click', cancelNewClass);
}

function hideAddNewClassInterface() {
    // Instead of reloading the page, restore the form properly
    const formGroup = document.querySelector('.form-group');
    
    formGroup.innerHTML = `
        <label for="class-type">Yoga Class Type</label>
        <select id="class-type" required>
            <option value="">Loading classes...</option>
        </select>
    `;
    
    // Re-assign the global reference
    window.classTypeSelect = document.getElementById('class-type');
    
    // Re-add event listener
    classTypeSelect.addEventListener('change', handleClassTypeChange);
    
    // Reload the classes
    loadYogaClasses();
}

async function saveNewClass() {
    const nameInput = document.getElementById('new-class-name');
    const descriptionInput = document.getElementById('new-class-description');
    
    const name = nameInput.value.trim();
    const description = descriptionInput.value.trim();
    
    if (!name || !description) {
        posthog.capture('add_class_error', {
            error_type: 'validation',
            has_name: !!name,
            has_description: !!description
        });
        alert('Please fill in both the class name and description');
        return;
    }
    
    // Track new class creation attempt
    posthog.capture('add_class_started', {
        class_name: name,
        description_length: description.length,
        timestamp: new Date().toISOString()
    });
    
    // Show loading state
    const saveBtn = document.getElementById('save-new-class');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    const startTime = Date.now();
    
    try {
        const response = await fetch(`${API_BASE_URL}/classes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        });
        
        const data = await response.json();
        const saveTime = Date.now() - startTime;
        
        if (data.success) {
            // Track successful class addition
            posthog.capture('add_class_success', {
                class_name: name,
                description_length: description.length,
                save_time_ms: saveTime,
                timestamp: new Date().toISOString()
            });
            
            // Success! Reload the classes and select the new one
            await loadYogaClasses();
            
            // Select the newly added class
            classTypeSelect.value = name;
            
            alert(`✅ Class "${name}" added successfully!`);
        } else {
            // Track class addition failure
            posthog.capture('add_class_error', {
                error_type: 'api_error',
                error_message: data.error,
                class_name: name,
                save_time_ms: saveTime
            });
            
            alert(`❌ Error: ${data.error}`);
        }
        
    } catch (error) {
        console.error('Error adding class:', error);
        
        // Track network error
        posthog.capture('add_class_error', {
            error_type: 'network_error',
            error_message: error.message,
            class_name: name,
            save_time_ms: Date.now() - startTime
        });
        
        alert('❌ Network error - please try again');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save & Use This Class';
    }
}

function cancelNewClass() {
    // Reload the page to restore the original dropdown
    location.reload();
}

async function checkSystemStatus() {
    // Check backend health
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('backend-status', 'Online', 'online');
        } else {
            updateStatus('backend-status', 'Issues', 'offline');
        }
    } catch (error) {
        console.error('Backend health check failed:', error);
        updateStatus('backend-status', 'Offline', 'offline');
    }
    
    // Check Spotify connection
    try {
        const response = await fetch(`${API_BASE_URL}/test-spotify`);
        const data = await response.json();
        
        if (data.success && data.connected) {
            updateStatus('spotify-status', 'Connected', 'online');
        } else {
            updateStatus('spotify-status', 'Not Connected', 'offline');
        }
    } catch (error) {
        console.error('Spotify check failed:', error);
        updateStatus('spotify-status', 'Error', 'offline');
    }
}

function updateStatus(elementId, text, statusClass) {
    const element = document.getElementById(elementId);
    element.textContent = text;
    element.className = `status-value ${statusClass}`;
}

async function loadYogaClasses() {
    try {
        const response = await fetch(`${API_BASE_URL}/classes`);
        const data = await response.json();
        
        if (data.success) {
            populateClassSelect(data.classes);
        } else {
            console.error('Failed to load classes:', data.error);
            classTypeSelect.innerHTML = '<option value="">Error loading classes</option>';
        }
    } catch (error) {
        console.error('Error loading classes:', error);
        classTypeSelect.innerHTML = '<option value="">Connection error</option>';
    }
}

function populateClassSelect(classes) {
    classTypeSelect.innerHTML = '<option value="">Select a class type...</option>';
    
    // Add existing classes
    classes.forEach(yogaClass => {
        const option = document.createElement('option');
        option.value = yogaClass.name;
        option.textContent = `${yogaClass.name} - ${yogaClass.description}`;
        classTypeSelect.appendChild(option);
    });

    // Add "Add New Class" option
    const addNewOption = document.createElement('option');
    addNewOption.value = '__ADD_NEW__';
    addNewOption.textContent = '➕ Add New Class...';
    classTypeSelect.appendChild(addNewOption);
}

async function handlePlaylistGeneration(event) {
    event.preventDefault();
    
    const formData = {
        class_name: classTypeSelect.value,
        music_preferences: musicPreferences.value,
        duration: parseInt(durationSlider.value)
    };
    
    // Validate form
    if (!formData.class_name || !formData.music_preferences) {
        // Track validation error
        posthog.capture('playlist_generation_error', {
            error_type: 'validation',
            missing_fields: {
                class_name: !formData.class_name,
                music_preferences: !formData.music_preferences
            }
        });

        alert('Please fill in all required fields');
        return;
    }
    
    // Track playlist generation start
    posthog.capture('playlist_generation_started', {
        class_name: formData.class_name,
        duration: formData.duration,
        music_preferences_length: formData.music_preferences.length,
        timestamp: new Date().toISOString()
    });
    
    // Show loading state
    setGeneratingState(true);
    const startTime = Date.now();

    try {
        const response = await fetch(`${API_BASE_URL}/generate-playlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            const generationTime = Date.now() - startTime;
            
            // Track successful generation
            posthog.capture('playlist_generation_success', {
                class_name: formData.class_name,
                duration: formData.duration,
                generation_time_ms: generationTime,
                spotify_tracks_found: data.spotify_integration?.search_results?.found_count || 0,
                spotify_tracks_total: data.spotify_integration?.search_results?.total_tracks || 0,
                ready_for_export: data.ready_for_export,
                timestamp: new Date().toISOString()
            });
                    
            displayPlaylistResult(data);
            currentPlaylistData = data;
            
            // Show export section if Spotify tracks were found
            if (data.ready_for_export) {
                showExportSection(formData.class_name);
            }
        } else {
            // Track generation failure
            posthog.capture('playlist_generation_error', {
                error_type: 'api_error',
                error_message: data.error,
                class_name: formData.class_name,
                duration: formData.duration,
                generation_time_ms: Date.now() - startTime
            });
            displayError(data.error || 'Failed to generate playlist');
        }
        
    } catch (error) {
        console.error('Error generating playlist:', error);
        
        // Track network error
        posthog.capture('playlist_generation_error', {
            error_type: 'network_error',
            error_message: error.message,
            class_name: formData.class_name,
            duration: formData.duration,
            generation_time_ms: Date.now() - startTime
        });
   
        displayError('Network error - please check your connection');
    } finally {
        setGeneratingState(false);
    }
}

function setGeneratingState(isGenerating) {
    generateBtn.disabled = isGenerating;
    if (isGenerating) {
        generateBtn.classList.add('loading');
    } else {
        generateBtn.classList.remove('loading');
    }
}

function displayPlaylistResult(data) {
    // Debug log to see what we're getting
    console.log('Playlist data received:', data);
    
    // Handle spotify integration data safely
    let spotifyInfo = "No Spotify data";
    if (data.spotify_integration && data.spotify_integration.search_results) {
        const found = data.spotify_integration.search_results.found_count || 0;
        const total = data.spotify_integration.search_results.total_tracks || 0;
        spotifyInfo = `${found}/${total} tracks found`;
    }
    
    const resultHtml = `
        <div class="playlist-result">
            <h3>🎵 Generated Playlist</h3>
            <div class="playlist-content">
                ${data.playlist}
            </div>
        </div>
    `;
    
    outputContent.innerHTML = resultHtml;
}

function displayError(message) {
    outputContent.innerHTML = `
        <div class="error-message" style="color: #d32f2f; text-align: center; padding: 20px;">
            <h3>❌ Error</h3>
            <p>${message}</p>
            <p style="margin-top: 10px; font-size: 0.9rem; color: #666;">
                Please try again or check your connection.
            </p>
        </div>
    `;
}

function showExportSection(className) {
    // Create unique playlist name with date
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0]; // YYYY-MM-DD format
    playlistNameInput.value = `${className} - ${dateStr}`;
    
    // Show spotify integration info in export section
    let spotifyInfo = "No Spotify data";
    if (currentPlaylistData && currentPlaylistData.spotify_integration && currentPlaylistData.spotify_integration.search_results) {
        const found = currentPlaylistData.spotify_integration.search_results.found_count || 0;
        const total = currentPlaylistData.spotify_integration.search_results.total_tracks || 0;
        spotifyInfo = `${found}/${total} tracks found on Spotify`;
    }
    
    // Update the export panel with Spotify info
    const exportPanel = document.querySelector('.export-panel');
    exportPanel.innerHTML = `
        <h3>🎵 Export to Spotify</h3>
        <p><strong>Spotify Integration:</strong> ${spotifyInfo}</p>
        <p>Your playlist is ready! Click below to create it in your Spotify account.</p>
        <div class="export-controls">
            <label for="playlist-name">Playlist Name:</label>
            <input type="text" id="playlist-name" placeholder="Enter playlist name" value="${playlistNameInput.value}">
            <button id="export-btn" class="export-btn">Create Spotify Playlist</button>
        </div>
        <div id="export-result"></div>
    `;
    
    // Re-get the elements since we just recreated them
    const newPlaylistNameInput = document.getElementById('playlist-name');
    const newExportBtn = document.getElementById('export-btn');
    const newExportResult = document.getElementById('export-result');
    
    // Update global references
    window.playlistNameInput = newPlaylistNameInput;
    window.exportBtn = newExportBtn;
    window.exportResult = newExportResult;
    
    // Re-attach event listener
    newExportBtn.addEventListener('click', handleSpotifyExport);
    
    exportSection.style.display = 'block';
}

async function handleSpotifyExport() {
    const currentPlaylistNameInput = document.getElementById('playlist-name');
    const currentExportBtn = document.getElementById('export-btn');
    const currentExportResult = document.getElementById('export-result');
    
    console.log('Export button clicked');
    
    if (!currentPlaylistData || !currentPlaylistData.spotify_integration) {
        displayExportError('No playlist data available for export');
        return;
    }
    
    const playlistName = currentPlaylistNameInput.value.trim();
    if (!playlistName) {
        alert('Please enter a playlist name');
        return;
    }
    
    // Get track IDs
    let trackIds = [];
    if (currentPlaylistData.spotify_integration.track_ids) {
        trackIds = currentPlaylistData.spotify_integration.track_ids;
    } else if (currentPlaylistData.spotify_integration.search_results && 
               currentPlaylistData.spotify_integration.search_results.successful_tracks) {
        trackIds = currentPlaylistData.spotify_integration.search_results.successful_tracks.map(
            track => track.spotify_data.spotify_id
        );
    }
    
    if (trackIds.length === 0) {
        displayExportError('No Spotify tracks available for export');
        return;
    }
    
    // Check if we have an auth code from URL (user returning from Spotify)
    const authCode = getSpotifyAuthCodeFromURL();
    
    if (authCode) {
        // User has returned from Spotify authorization - create playlist
        await createPlaylistWithAuthCode(playlistName, trackIds, authCode);
    } else {
        // No auth code - need to get Spotify authorization first
        await initiateSpotifyAuth(playlistName, trackIds);
    }
}

async function initiateSpotifyAuth(playlistName, trackIds) {
    const currentExportBtn = document.getElementById('export-btn');
    const currentExportResult = document.getElementById('export-result');
    
    try {
        // Show loading state
        currentExportBtn.disabled = true;
        currentExportBtn.textContent = '🔄 Getting Spotify Authorization...';
        
        // Get Spotify authorization URL
        const response = await fetch(`${API_BASE_URL}/create-spotify-playlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'get_auth_url'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.auth_url) {
            // Store playlist data in localStorage for when user returns
            localStorage.setItem('pendingPlaylist', JSON.stringify({
                playlistName: playlistName,
                trackIds: trackIds
            }));
            
            // Show user instructions
            currentExportResult.className = 'info';
            currentExportResult.innerHTML = `
                <strong>🎵 Spotify Authorization Required</strong><br>
                Click the button below to authorize with Spotify, then return to create your playlist.
                <br><br>
                <a href="${data.auth_url}" class="spotify-auth-btn">
                    Authorize with Spotify
                </a>
                <br><br>
                <button onclick="checkForSpotifyReturn()" class="check-return-btn">
                    I've Authorized - Create Playlist Now
                </button>
            `;
            
        } else {
            displayExportError(data.error || 'Failed to get Spotify authorization URL');
        }
        
    } catch (error) {
        console.error('Error getting Spotify auth:', error);
        displayExportError('Network error - please try again');
    } finally {
        currentExportBtn.disabled = false;
        currentExportBtn.textContent = 'Create Spotify Playlist';
    }
}

async function createPlaylistWithAuthCode(playlistName, trackIds, authCode) {
    const currentExportBtn = document.getElementById('export-btn');
    const currentExportResult = document.getElementById('export-result');
    
    try {
        // Show loading state
        currentExportBtn.disabled = true;
        currentExportBtn.textContent = '🔄 Creating Spotify Playlist...';
        
        const response = await fetch(`${API_BASE_URL}/create-spotify-playlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'create_playlist',
                playlist_name: playlistName,
                track_ids: trackIds,
                auth_code: authCode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentExportResult.className = 'success';
            currentExportResult.innerHTML = `
                <strong>🎉 Success!</strong><br>
                ${data.message}<br>
                <a href="${data.playlist_url}" target="_blank">Open in Spotify</a>
            `;
            
            // Clear stored playlist data
            localStorage.removeItem('pendingPlaylist');
            
        } else if (data.needs_auth) {
            // Still needs authorization
            await initiateSpotifyAuth(playlistName, trackIds);
        } else {
            displayExportError(data.error || 'Failed to create playlist');
        }
        
    } catch (error) {
        console.error('Error creating Spotify playlist:', error);
        displayExportError('Network error - please try again');
    } finally {
        currentExportBtn.disabled = false;
        currentExportBtn.textContent = 'Create Spotify Playlist';
    }
}

function getSpotifyAuthCodeFromURL() {
    // Check if there's an auth code in the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
        // Clean up the URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return code;
    }
    
    return null;
}

function checkForSpotifyReturn() {
    // Check if user has returned from Spotify authorization
    const authCode = getSpotifyAuthCodeFromURL();
    const pendingPlaylist = localStorage.getItem('pendingPlaylist');
    
    if (authCode && pendingPlaylist) {
        const playlistData = JSON.parse(pendingPlaylist);
        createPlaylistWithAuthCode(playlistData.playlistName, playlistData.trackIds, authCode);
    } else if (!authCode) {
        alert('No authorization code found. Please make sure you completed the Spotify authorization.');
    } else {
        alert('No pending playlist found. Please try creating a playlist again.');
    }
}

function displayExportSuccess(message) {
    exportResult.className = 'success';
    exportResult.innerHTML = `
        <strong>🎉 Success!</strong><br>
        ${message}
    `;
}

function displayExportError(message) {
    exportResult.className = 'error';
    exportResult.innerHTML = `
        <strong>❌ Error:</strong><br>
        ${message}
    `;
}

// Utility function for debugging
window.debugAPI = async function() {
    console.log('=== API Debug Info ===');
    
    try {
        const health = await fetch(`${API_BASE_URL}/health`).then(r => r.json());
        console.log('Health:', health);
        
        const classes = await fetch(`${API_BASE_URL}/classes`).then(r => r.json());
        console.log('Classes:', classes);
        
        const spotify = await fetch(`${API_BASE_URL}/test-spotify`).then(r => r.json());
        console.log('Spotify:', spotify);
        
    } catch (error) {
        console.error('Debug failed:', error);
    }
};