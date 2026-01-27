---
layout: planexe_empty_page
title: Execute
permalink: /execute/
---

<header class="post-header planexe-usecases-header">
<h1 class="post-title">Execute</h1>
<div class="header-description">
    <p class="subtitle">The goal is to execute a plan.</p>
    <p class="description">Contact on Discord if you are interested in helping out with this.</p>
</div>
</header>

<div class="px-callout">
  <h2>Execute with parameters</h2>
  <div id="url-params-display" class="px-codebox">Loading parameters...</div>
  <p class="px-note">
    Try adding parameters to the URL like:
    <code>?plan_id=78773f12-2c73-49b1-a750-d03022a821ed&priority=high&status=active</code>
  </p>
</div>

<script>
    /**
     * URL Parameter Extraction Utilities
     * Functions to extract and parse URL-encoded parameters
     */

    /**
     * Extracts URL parameters from the current page URL
     * @returns {Object} Object containing parameter key-value pairs
     */
    function getUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {};
        
        for (const [key, value] of urlParams) {
            params[key] = decodeURIComponent(value);
        }
        
        return params;
    }

    /**
     * Gets a specific parameter value from the current page URL
     * @param {string} paramName - The name of the parameter to extract
     * @returns {string|null} The parameter value or null if not found
     */
    function getUrlParam(paramName) {
        const urlParams = new URLSearchParams(window.location.search);
        const value = urlParams.get(paramName);
        return value ? decodeURIComponent(value) : null;
    }

    /**
     * Checks if a parameter exists in the current page URL
     * @param {string} paramName - The name of the parameter to check
     * @returns {boolean} True if the parameter exists, false otherwise
     */
    function hasUrlParam(paramName) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.has(paramName);
    }

    /**
     * Builds a URL with parameters from an object
     * @param {string} baseUrl - The base URL
     * @param {Object} params - Object containing parameter key-value pairs
     * @returns {string} The complete URL with parameters
     */
    function buildUrlWithParams(baseUrl, params) {
        try {
            const url = new URL(baseUrl);
            
            for (const [key, value] of Object.entries(params)) {
                if (value !== null && value !== undefined) {
                    url.searchParams.set(key, encodeURIComponent(value));
                }
            }
            
            return url.toString();
        } catch (error) {
            console.error('Error building URL:', error);
            return baseUrl;
        }
    }

    // Display URL parameters when page loads
    function displayUrlParams() {
        const params = getUrlParams();
        const displayElement = document.getElementById('url-params-display');
        
        if (Object.keys(params).length === 0) {
            displayElement.textContent = 'No URL parameters found.';
            displayElement.style.color = '#6c757d';
        } else {
            displayElement.textContent = JSON.stringify(params, null, 2);
            displayElement.style.color = '#000';
        }
    }

    // Initialize when page loads
    window.addEventListener('load', displayUrlParams);
    
    // Also display immediately if DOM is already ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', displayUrlParams);
    } else {
        displayUrlParams();
    }
</script>
