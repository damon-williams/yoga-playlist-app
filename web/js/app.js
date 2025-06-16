// PostHog is now enabled
// To disable, uncomment the following:
/*
window.posthog = {
    capture: function() {
        console.log('PostHog disabled - would have tracked:', arguments);
    }
};
*/

// Safe PostHog capture function
function captureEvent(eventName, properties) {
    if (typeof posthog !== 'undefined' && posthog.capture) {
        posthog.capture(eventName, properties);
    } else {
        console.log('PostHog not ready - would have tracked:', eventName, properties);
    }
}

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
    captureEvent('app_loaded', {
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent
    });

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
        // User has returned from Spotify - create the playlist
        console.log('🎵 Spotify authorization complete, creating playlist...');
        try {
            const playlistData = JSON.parse(pendingPlaylist);
            // Small delay to ensure page is ready
            setTimeout(() => {
                createSpotifyPlaylist(playlistData.playlistName, playlistData.trackIds, authCode);
            }, 1000);
        } catch (error) {
            console.error('Error processing playlist data:', error);
            showSuccessMessage('❌ Error creating playlist. Please try again.', true);
            localStorage.removeItem('pendingPlaylist');
        }
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

// Handle class card selection
window.selectClassCard = function(card) {
    // Skip if this is the custom card
    if (card.classList.contains('add-custom-card')) {
        return;
    }
    
    // Remove previous selection
    document.querySelectorAll('.class-card').forEach(c => {
        c.classList.remove('selected');
        c.style.background = 'rgba(255, 255, 255, 0.1)';
        c.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    });
    
    // Highlight selected card
    card.classList.add('selected');
    card.style.background = 'rgba(103, 58, 183, 0.3)';
    card.style.borderColor = 'rgba(103, 58, 183, 0.8)';
    
    // Set hidden input value
    const className = card.getAttribute('data-class-name');
    const description = card.getAttribute('data-description');
    const hiddenInput = document.getElementById('class-type');
    console.log('🎯 Card clicked - className:', className);
    console.log('🎯 Card clicked - description:', description);
    console.log('🎯 Card clicked - hiddenInput found:', !!hiddenInput);
    
    if (hiddenInput) {
        hiddenInput.value = className;
        console.log('🎯 Card clicked - hiddenInput.value set to:', hiddenInput.value);
        // Trigger change event to notify fairydust button
        hiddenInput.dispatchEvent(new Event('change'));
    }
    
    // Pre-populate music preferences with class description from database
    console.log('🎵 Trying to update music preferences for class:', className);
    console.log('🎵 Class description:', description);
    
    // Use a small delay to ensure DOM is ready
    setTimeout(() => {
        const musicPreferencesElement = document.getElementById('music-preferences');
        console.log('🎵 Music element found:', !!musicPreferencesElement);
        
        if (musicPreferencesElement && description) {
            musicPreferencesElement.value = description;
            console.log('✅ Updated music preferences to class description:', description);
        } else if (musicPreferencesElement) {
            musicPreferencesElement.value = '';
            console.log('🔄 Cleared music preferences (no description available)');
        } else {
            console.error('❌ Could not find music-preferences element!');
        }
    }, 50);
    
    // Button update is handled by the change event now
};

// Handle add custom class
window.handleAddCustomClass = function() {
    console.log('🔧 Custom class button clicked - checking authentication...');
    
    // Check if user is connected to fairydust
    let isConnected = false;
    
    // First check if fairydust SDK is loaded
    if (typeof Fairydust === 'undefined') {
        console.log('❌ fairydust SDK not loaded');
        showSuccessMessage('❌ fairydust SDK not loaded. Please refresh the page.', true);
        return;
    }
    
    // Try multiple ways to check authentication
    // 1. Check if we have stored user data from onConnect
    if (window.fairydustUser && window.fairydustUser.id) {
        console.log('✅ User authenticated via stored user data:', window.fairydustUser.id);
        isConnected = true;
    }
    
    // 2. Try the fairydust API if available
    if (!isConnected && window.fairydust && window.fairydust.getAPI) {
        try {
            const api = window.fairydust.getAPI();
            if (api.isAuthenticated && api.isAuthenticated()) {
                console.log('✅ User authenticated via fairydust API');
                isConnected = true;
            }
        } catch (error) {
            console.log('Could not check fairydust API:', error);
        }
    }
    
    // 3. Fallback: check DOM for authentication indicators
    if (!isConnected) {
        const accountDesktop = document.querySelector('#fairydust-account-desktop');
        const accountMobile = document.querySelector('#fairydust-account-mobile');
        
        isConnected = (accountDesktop && (accountDesktop.textContent.includes('DUST') || accountDesktop.textContent.includes('@'))) || 
                     (accountMobile && (accountMobile.textContent.includes('DUST') || accountMobile.textContent.includes('@')));
        
        if (isConnected) {
            console.log('✅ User authenticated via DOM check');
        }
    }
    
    console.log('🔧 Final authentication result:', isConnected);
    
    if (!isConnected) {
        showSuccessMessage('🔐 Please connect with fairydust (top right) to add custom class types. Custom classes are tied to your account.', true);
        
        // Pulse the account component to draw attention
        const accountDesktop = document.querySelector('#fairydust-account-desktop');
        const accountMobile = document.querySelector('#fairydust-account-mobile');
        [accountDesktop, accountMobile].forEach(component => {
            if (component) {
                component.style.animation = 'pulse 1s ease-in-out 3';
                setTimeout(() => {
                    component.style.animation = '';
                }, 3000);
            }
        });
        return;
    }
    
    // User is connected, show the custom class interface
    console.log('✅ Showing custom class interface');
    showAddNewClassInterface();
};

function handleClassTypeChange() {
    // This function is no longer needed with cards
}

function showAddNewClassInterface() {
    // Get the class type form group (first one)
    const classTypeFormGroup = document.querySelector('.form-group');
    
    // Hide the music preferences form group
    const musicPreferencesFormGroup = document.querySelector('#music-preferences').closest('.form-group');
    if (musicPreferencesFormGroup) {
        musicPreferencesFormGroup.style.display = 'none';
    }
    
    // Replace the class type form group with custom class input fields
    classTypeFormGroup.innerHTML = `
        <label>Add Custom Class Type</label>
        <div class="custom-class-form-container">
            <div class="custom-class-form-group">
                <label for="new-class-name" class="custom-class-form-label">Class Name</label>
                <input type="text" id="new-class-name" class="custom-class-form-input" placeholder="e.g., Hot Power Flow" required>
            </div>
            
            <div class="custom-class-form-group">
                <label for="new-class-description" class="custom-class-form-label">Class Description</label>
                <textarea id="new-class-description" class="custom-class-form-textarea" placeholder="Describe the style, intensity, and focus of this class..." required></textarea>
            </div>
            
            <div class="custom-class-form-actions">
                <button type="button" id="save-new-class" class="custom-class-save-btn">💾 Save & Use This Class</button>
                <button type="button" id="cancel-new-class" class="custom-class-cancel-btn">❌ Cancel</button>
            </div>
        </div>
        <input type="hidden" id="class-type" required>
    `;
    
    // Re-assign the global reference to the hidden input
    window.classTypeSelect = document.getElementById('class-type');
    
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
        captureEvent('add_class_error', {
            error_type: 'validation',
            has_name: !!name,
            has_description: !!description
        });
        alert('Please fill in both the class name and description');
        return;
    }
    
    // Track new class creation attempt
    captureEvent('add_class_started', {
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
        // Get user ID for custom class
        const userId = getFairydustUserId();
        if (!userId) {
            showSuccessMessage('❌ User authentication required to create custom classes.', true);
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/classes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description,
                user_id: userId,
                is_public: false  // Custom classes are private by default
            })
        });
        
        const data = await response.json();
        const saveTime = Date.now() - startTime;
        
        if (data.success) {
            // Track successful class addition
            captureEvent('add_class_success', {
                class_name: name,
                description_length: description.length,
                save_time_ms: saveTime,
                timestamp: new Date().toISOString()
            });
            
            // Success! Reload the classes
            await loadYogaClasses();
            
            // Show success message
            showSuccessMessage(`✅ Class "${name}" added successfully! You can now select it from the class cards.`, false);
            
            // Auto-select the newly added class after cards load
            setTimeout(() => {
                const newCard = document.querySelector(`[data-class-name="${name}"]`);
                if (newCard) {
                    selectClassCard(newCard);
                }
            }, 500);
        } else {
            // Track class addition failure
            captureEvent('add_class_error', {
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
        captureEvent('add_class_error', {
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
    // Reload the classes to restore the card interface
    loadYogaClasses();
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
    if (element) {
        element.textContent = text;
        element.className = `status-value ${statusClass}`;
    } else {
        console.log(`Status update: ${elementId} - ${text} (${statusClass})`);
    }
}

async function loadYogaClasses() {
    try {
        // Get fairydust user ID if available
        const userId = getFairydustUserId();
        const url = userId ? `${API_BASE_URL}/classes?user_id=${encodeURIComponent(userId)}` : `${API_BASE_URL}/classes`;
        
        console.log('🔍 Loading classes for user:', userId || 'anonymous');
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            populateClassSelect(data.classes);
        } else {
            console.error('Failed to load classes:', data.error);
            // Show error in the loading area
            const loadingDiv = document.getElementById('class-type-loading');
            if (loadingDiv) {
                loadingDiv.textContent = 'Error loading classes';
                loadingDiv.style.color = '#d32f2f';
            }
        }
    } catch (error) {
        console.error('Error loading classes:', error);
        const loadingDiv = document.getElementById('class-type-loading');
        if (loadingDiv) {
            loadingDiv.textContent = 'Connection error';
            loadingDiv.style.color = '#d32f2f';
        }
    }
}

// Helper function to get fairydust user ID
function getFairydustUserId() {
    // Try to get user ID from the fairydust SDK
    if (window.fairydust && window.fairydust.getAPI) {
        try {
            const api = window.fairydust.getAPI();
            if (api.isAuthenticated && api.isAuthenticated()) {
                // Try to get user info from the API
                const user = api.getCurrentUser ? api.getCurrentUser() : null;
                if (user && user.id) {
                    return user.id;
                }
            }
        } catch (error) {
            console.log('Could not get user from fairydust API:', error);
        }
    }
    
    // Fallback: try to extract user ID from the global fairydust events/callbacks
    // The user data is logged in console as: {id: '9b061774-85a0-4d5a-9a6a-bb81dc6ac61b', ...}
    // We could store this in a global variable when the onConnect callback fires
    if (window.fairydustUser && window.fairydustUser.id) {
        return window.fairydustUser.id;
    }
    
    return null;
}

function populateClassSelect(classes) {
    // Save the currently selected class name before rebuilding
    const currentSelection = document.getElementById('class-type')?.value;
    console.log('🔄 Preserving class selection:', currentSelection);
    
    // Get the form group container - try multiple approaches since form structure may have changed
    let formGroup = null;
    
    if (classTypeSelect && classTypeSelect.closest) {
        formGroup = classTypeSelect.closest('.form-group');
    }
    
    // Fallback: get the first form group if the above failed
    if (!formGroup) {
        formGroup = document.querySelector('.form-group');
    }
    
    if (!formGroup) {
        console.error('Could not find form group for class selection');
        return;
    }
    
    // Show music preferences form group if it was hidden
    const musicPreferencesFormGroup = document.querySelector('#music-preferences')?.closest('.form-group');
    if (musicPreferencesFormGroup) {
        musicPreferencesFormGroup.style.display = 'block';
    }
    
    // Separate public and custom classes
    const publicClasses = classes.filter(c => !c.is_custom);
    const customClasses = classes.filter(c => c.is_custom);
    
    console.log('📋 Showing classes - Public:', publicClasses.length, 'Custom:', customClasses.length);
    
    // Replace select with card grid
    formGroup.innerHTML = `
        <label>Choose Your Class Type</label>
        <div class="class-cards-grid" style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-top: 10px;
        ">
            ${publicClasses.map(yogaClass => `
                <div 
                    class="class-card" 
                    data-class-name="${yogaClass.name}"
                    data-description="${yogaClass.description}"
                    onclick="selectClassCard(this)"
                    style="
                        padding: 20px 15px;
                        background: rgba(255, 255, 255, 0.1);
                        border: 2px solid rgba(255, 255, 255, 0.2);
                        border-radius: 12px;
                        text-align: center;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        font-weight: 500;
                        backdrop-filter: blur(10px);
                    "
                    onmouseover="this.style.background='rgba(255, 255, 255, 0.15)'; this.style.transform='translateY(-2px)'"
                    onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'; this.style.transform='translateY(0)'"
                >
                    ${yogaClass.name}
                </div>
            `).join('')}
            
            ${customClasses.map(yogaClass => `
                <div 
                    class="class-card custom-class" 
                    data-class-name="${yogaClass.name}"
                    data-description="${yogaClass.description}"
                    onclick="selectClassCard(this)"
                    style="
                        padding: 20px 15px;
                        background: rgba(255, 255, 255, 0.1);
                        border: 2px solid rgba(255, 255, 255, 0.2);
                        border-radius: 12px;
                        text-align: center;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        font-weight: 500;
                        backdrop-filter: blur(10px);
                        position: relative;
                    "
                    onmouseover="this.style.background='rgba(103, 58, 183, 0.15)'; this.style.borderColor='rgba(103, 58, 183, 0.4)'; this.style.transform='translateY(-2px)'"
                    onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'; this.style.borderColor='rgba(255, 255, 255, 0.2)'; this.style.transform='translateY(0)'"
                >
                    ${yogaClass.name}
                    <div style="position: absolute; top: 5px; right: 5px; font-size: 0.7rem; opacity: 0.8;">✨</div>
                </div>
            `).join('')}
            
            <div 
                class="class-card add-custom-card" 
                onclick="handleAddCustomClass()"
                style="
                    padding: 20px 15px;
                    background: transparent;
                    border: 2px dashed rgba(255, 255, 255, 0.3);
                    border-radius: 12px;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    opacity: 0.7;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 5px;
                "
                onmouseover="this.style.opacity='1'; this.style.borderColor='rgba(255, 255, 255, 0.5)'"
                onmouseout="this.style.opacity='0.7'; this.style.borderColor='rgba(255, 255, 255, 0.3)'"
            >
                <span style="font-size: 1.2rem;">+</span> Custom
            </div>
        </div>
        <input type="hidden" id="class-type" required>
    `;
    
    // Re-assign the global reference to the hidden input
    window.classTypeSelect = document.getElementById('class-type');
    
    // Restore the previous selection if it exists
    if (currentSelection) {
        console.log('🔄 Restoring class selection:', currentSelection);
        const cardToSelect = document.querySelector(`[data-class-name="${currentSelection}"]`);
        if (cardToSelect) {
            // Use setTimeout to ensure DOM is fully rendered
            setTimeout(() => {
                selectClassCard(cardToSelect);
                console.log('✅ Class selection restored');
            }, 100);
        }
    }
}

async function handlePlaylistGeneration(event) {
    event.preventDefault();
    
    // Get fresh reference to the class type input (in case DOM was rebuilt)
    const classTypeInput = document.getElementById('class-type');
    const selectedClassName = classTypeInput ? classTypeInput.value : '';
    
    // Get the selected class card's description
    const selectedCard = document.querySelector('.class-card[data-class-name="' + selectedClassName + '"]');
    const classDescription = selectedCard ? selectedCard.getAttribute('data-description') : '';

    const formData = {
        class_name: selectedClassName,
        class_description: classDescription,
        music_preferences: musicPreferences.value,
        duration: parseInt(durationSlider.value)
    };

    // Validate form
    console.log('🔍 Form validation - classTypeInput.value:', selectedClassName);
    console.log('🔍 Form validation - formData.class_name:', formData.class_name);
    
    if (!formData.class_name) {
        // Track validation error
        captureEvent('playlist_generation_error', {
            error_type: 'validation',
            missing_fields: {
                class_name: !formData.class_name
            }
        });

        showSuccessMessage('❌ Please select a class type by clicking on one of the class cards above', true);
        return;
    }
    
    // Track playlist generation start
    captureEvent('playlist_generation_started', {
        class_name: formData.class_name,
        duration: formData.duration,
        music_preferences_length: formData.music_preferences.length,
        timestamp: new Date().toISOString()
    });
    
    // Show loading state
    setGeneratingState(true);
    showLoadingAnimation(); 
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
            captureEvent('playlist_generation_success', {
                class_name: formData.class_name,
                duration: formData.duration,
                generation_time_ms: generationTime,
                spotify_tracks_found: data.spotify_integration?.search_results?.found_count || 0,
                spotify_tracks_total: data.spotify_integration?.search_results?.total_tracks || 0,
                ready_for_export: data.ready_for_export,
                timestamp: new Date().toISOString()
            });
            
            // Store the data for later reveal
            currentPlaylistData = data;
            
            // Show celebration screen first!
            showPlaylistReadyScreen(data, formData.class_name);

        } else {
            // Track generation failure
            captureEvent('playlist_generation_error', {
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
        captureEvent('playlist_generation_error', {
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
    // The generate button is now handled by fairydust SDK
    // We can find the actual button element that was created
    const fairydustButton = document.querySelector('#fairydust-generate-button button');
    
    if (fairydustButton) {
        fairydustButton.disabled = isGenerating;
        if (isGenerating) {
            fairydustButton.classList.add('loading');
        } else {
            fairydustButton.classList.remove('loading');
        }
    }
    
    // Also handle the legacy generateBtn reference if it exists
    if (generateBtn) {
        generateBtn.disabled = isGenerating;
        if (isGenerating) {
            generateBtn.classList.add('loading');
        } else {
            generateBtn.classList.remove('loading');
        }
    }
}

// Simple function to create Spotify playlist
async function createSpotifyPlaylist(playlistName, trackIds, authCode) {
    try {
        showSuccessMessage('🔄 Creating your Spotify playlist...');
        
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
            showSuccessMessage(`🎉 Success! Created playlist "${playlistName}". <a href="${data.playlist_url}" target="_blank">Open in Spotify</a>`);
            localStorage.removeItem('pendingPlaylist');
            
            // Update export button UI if visible
            const exportBtn = document.getElementById('export-btn');
            if (exportBtn) {
                exportBtn.disabled = false;
                exportBtn.textContent = 'Create Spotify Playlist';
            }
            
            // Update export result if visible
            const exportResult = document.getElementById('export-result');
            if (exportResult) {
                exportResult.className = 'success';
                exportResult.innerHTML = `
                    <strong>🎉 Success!</strong><br>
                    <a href="${data.playlist_url}" target="_blank">Open in Spotify</a>
                `;
            }
        } else if (data.needs_auth) {
            // This shouldn't happen if we have an auth code, but just in case
            await initiateSpotifyAuth(playlistName, trackIds);
        } else {
            showSuccessMessage(`❌ Error: ${data.error || 'Failed to create playlist'}`, true);
            localStorage.removeItem('pendingPlaylist');
        }
        
    } catch (error) {
        console.error('Network error:', error);
        showSuccessMessage(`❌ Network error. Please try again.`, true);
        localStorage.removeItem('pendingPlaylist');
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
    
    // Clean up the playlist text formatting
    const formattedPlaylist = data.playlist
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Convert **text** to <strong>
        .replace(/BPM:/g, '<em>BPM:</em>')  // Style BPM info
        .replace(/Energy:/g, '<em>Energy:</em>');  // Style Energy info
    
    const resultHtml = `
        <div class="playlist-result">
            <h3>🎵 Your Personalized Playlist</h3>
            <div class="playlist-content">
                ${formattedPlaylist}
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
        <p>${spotifyInfo}</p>
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
    
    // Get track IDs - ensure they're in the correct format
    let trackIds = [];
    if (currentPlaylistData.spotify_integration.track_ids) {
        trackIds = currentPlaylistData.spotify_integration.track_ids;
    } else if (currentPlaylistData.spotify_integration.search_results && 
               currentPlaylistData.spotify_integration.search_results.successful_tracks) {
        trackIds = currentPlaylistData.spotify_integration.search_results.successful_tracks.map(
            track => {
                // Ensure we have the full Spotify URI
                const id = track.spotify_data.spotify_id;
                return id.startsWith('spotify:track:') ? id : `spotify:track:${id}`;
            }
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
        await createSpotifyPlaylist(playlistName, trackIds, authCode);
    } else {
        // No auth code - need to get Spotify authorization first
        await initiateSpotifyAuth(playlistName, trackIds);
    }
}

async function initiateSpotifyAuth(playlistName, trackIds) {
    const currentExportBtn = document.getElementById('export-btn');
    
    try {
        // Show loading state
        currentExportBtn.disabled = true;
        currentExportBtn.textContent = '🔄 Getting Spotify Authorization...';
        
        // Store playlist data in localStorage for when user returns
        const pendingData = {
            playlistName: playlistName,
            trackIds: trackIds,
            timestamp: Date.now()
        };
        console.log('💾 Storing pending playlist data:', pendingData);
        localStorage.setItem('pendingPlaylist', JSON.stringify(pendingData));
        
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
            // Directly redirect to Spotify (no second button)
            window.location.href = data.auth_url;
        } else {
            displayExportError(data.error || 'Failed to get Spotify authorization URL');
            currentExportBtn.disabled = false;
            currentExportBtn.textContent = 'Create Spotify Playlist';
        }
        
    } catch (error) {
        console.error('Error getting Spotify auth:', error);
        displayExportError('Network error - please try again');
        currentExportBtn.disabled = false;
        currentExportBtn.textContent = 'Create Spotify Playlist';
    }
}

// Show loading animation in output panel
function showLoadingAnimation() {
    outputContent.innerHTML = `
        <div class="loading-animation">
            <div class="loading-spinner"></div>
            <div class="loading-text">🎵 Generating your playlist...</div>
            <div class="loading-subtext">Finding the perfect tracks on Spotify</div>
        </div>
    `;
}

// Show celebration screen before revealing playlist
function showPlaylistReadyScreen(data, className) {
    // Get track count for excitement
    let trackCount = 0;
    if (data.spotify_integration?.search_results?.found_count) {
        trackCount = data.spotify_integration.search_results.found_count;
    }
    
    outputContent.innerHTML = `
        <div class="playlist-ready-celebration">
            <div 
                class="celebration-gift-icon"
                onclick="revealPlaylist()" 
                title="Click to unwrap your playlist!"
            >
                🎁
            </div>
            
            <h2 class="celebration-title">
                Playlist Ready!
            </h2>
            
            <p class="celebration-subtitle">
                Your personalized <strong>${className}</strong> playlist is complete<br>
                ${trackCount > 0 ? `with ${trackCount} perfect tracks` : 'with curated tracks'}
            </p>
            
            <div class="celebration-actions">
                <button 
                    onclick="revealPlaylist()" 
                    class="celebration-btn-primary"
                >
                    ✨ Show My Playlist
                </button>
                
                <button 
                    onclick="autoReveal()" 
                    class="celebration-btn-secondary"
                >
                    🔮 Surprise Me (auto-reveal in 3s)
                </button>
            </div>
        </div>
    `;
}

// Global functions for the celebration buttons
window.revealPlaylist = function() {
    if (currentPlaylistData) {
        displayPlaylistResult(currentPlaylistData);
        showExportAndShareSections();
    }
};

window.autoReveal = function() {
    // Add a little countdown excitement
    const button = event.target;
    let countdown = 3;
    button.textContent = `🔮 Revealing in ${countdown}...`;
    button.disabled = true;
    
    const timer = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            button.textContent = `🔮 Revealing in ${countdown}...`;
        } else {
            clearInterval(timer);
            revealPlaylist();
        }
    }, 1000);
};

function showExportAndShareSections() {
    if (currentPlaylistData) {
        // Show export section if Spotify tracks were found
        if (currentPlaylistData.ready_for_export) {
            showExportSection(currentPlaylistData.class_name || 'Yoga Playlist');
        }
        // Show share section
        showShareSection();
    }
}

// Show share section
function showShareSection() {
    const shareSection = document.getElementById('share-section');
    if (shareSection) {
        shareSection.style.display = 'block';
        
        // Add event listeners for share buttons
        document.getElementById('copy-link-btn').addEventListener('click', copyAppLink);
        document.getElementById('share-twitter-btn').addEventListener('click', shareOnTwitter);
        document.getElementById('share-linkedin-btn').addEventListener('click', shareOnLinkedIn);
    }
}

// Share functions
function copyAppLink() {
    const url = window.location.origin;
    navigator.clipboard.writeText(url).then(() => {
        const btn = document.getElementById('copy-link-btn');
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        btn.style.background = '#4CAF50';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    });
}

function shareOnTwitter() {
    const text = "Check out this amazing AI-powered yoga playlist generator! 🧘‍♀️🎵 Creates personalized Spotify playlists for yoga classes.";
    const url = window.location.origin;
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
    window.open(twitterUrl, '_blank');
}

function shareOnLinkedIn() {
    const url = window.location.origin;
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
    window.open(linkedinUrl, '_blank');
}


// Add this function to show success messages
function showSuccessMessage(message, isError = false) {
    const successArea = document.getElementById('success-area');
    const successContent = document.getElementById('success-content');
    
    // Ensure elements exist before trying to use them
    if (!successArea || !successContent) {
        console.error('Success message elements not found, retrying...');
        // Retry after a short delay if elements aren't ready
        setTimeout(() => showSuccessMessage(message, isError), 500);
        return;
    }
    
    // Add dismiss button to message
    const messageWithDismiss = `
        <div class="success-message-container">
            <div class="success-message-content">${message}</div>
            <button onclick="dismissSuccessMessage()" class="success-dismiss-btn" title="Dismiss message">✕</button>
        </div>
    `;
    
    successContent.innerHTML = messageWithDismiss;
    successArea.className = isError ? 'success-area error' : 'success-area';
    successArea.style.display = 'block';
    
    // Scroll to top to ensure message is visible
    window.scrollTo(0, 0);
    
    // Remove auto-hide timeout - let user dismiss manually
}

// Function to dismiss success message
window.dismissSuccessMessage = function() {
    const successArea = document.getElementById('success-area');
    if (successArea) {
        successArea.style.display = 'none';
    }
};

// Removed - using createSpotifyPlaylist instead

function getSpotifyAuthCodeFromURL() {
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

// Removed manual trigger - keeping the flow simple

// Debug function to check Spotify auth state
window.debugSpotifyAuth = function() {
    console.log('=== Spotify Auth Debug Info ===');
    console.log('Current URL:', window.location.href);
    console.log('URL search params:', window.location.search);
    
    const urlParams = new URLSearchParams(window.location.search);
    console.log('Code in URL:', urlParams.get('code'));
    console.log('Error in URL:', urlParams.get('error'));
    
    console.log('Stored auth code:', localStorage.getItem('spotify_auth_code'));
    console.log('Pending playlist:', localStorage.getItem('pendingPlaylist'));
    console.log('Current playlist data available:', !!currentPlaylistData);
    
    if (currentPlaylistData) {
        console.log('Spotify integration data:', currentPlaylistData.spotify_integration);
    }
};

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