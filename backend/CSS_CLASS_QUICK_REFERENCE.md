# Bidding System - CSS Class Reference Guide

## Quick Reference for Using Modern Styling

---

## 🔘 Button Classes

### Primary Action Button
```html
<button class="btn-primary">Place Bid</button>

<!-- Full Width -->
<button class="btn-primary btn-full">Submit</button>

<!-- Disabled State (automatic via disabled attribute) -->
<button class="btn-primary" disabled>Loading...</button>
```
**Use for**: Main actions, form submissions, primary CTAs
**Colors**: Green gradient (#10b981 → #059669)
**Animation**: Ripple effect on hover

---

### Secondary Action Button
```html
<button class="btn-secondary">Cancel</button>
<a href="/back" class="btn-secondary">Back</a>
```
**Use for**: Cancel, go back, secondary actions
**Colors**: White background with green border
**Animation**: Color invert on hover

---

### Danger Action Button
```html
<button class="btn-danger">Delete Auction</button>
<button class="btn-danger">Withdraw Bid</button>
```
**Use for**: Destructive actions, deletions, risks
**Colors**: Red gradient (#ef4444 → #dc2626)
**Animation**: Elevated shadow on hover

---

## 📝 Form Classes

### Form Container
```html
<div class="form-container">
    <h2>Create Auction</h2>
    <!-- Form content -->
</div>
```
**Effect**: White card with shadow and border
**Padding**: 40px (responsive)

---

### Form Group (Field Container)
```html
<div class="form-group">
    <label>Field Name <span class="required">*</span></label>
    <input type="text" placeholder="Enter value">
    <span class="form-helper-text">Help text here</span>
</div>
```

### Form Error State
```html
<div class="form-group error">
    <label>Email Address</label>
    <input type="email" value="invalid">
    <span class="form-error">Please enter valid email</span>
</div>
```

---

### Form Row (Two Columns)
```html
<div class="form-row">
    <div class="form-group">
        <label>Starting Price</label>
        <input type="number">
    </div>
    <div class="form-group">
        <label>Minimum Bid</label>
        <input type="number">
    </div>
</div>

<!-- Full Width Row -->
<div class="form-row full">
    <div class="form-group">
        <label>Description</label>
        <textarea></textarea>
    </div>
</div>
```

---

### Input Types Supported
```html
<!-- Text Input -->
<input type="text" placeholder="Text here">

<!-- Number Input -->
<input type="number" min="0" step="100">

<!-- Email Input -->
<input type="email">

<!-- Date Input -->
<input type="date">

<!-- Select Dropdown -->
<select>
    <option>Option 1</option>
    <option>Option 2</option>
</select>

<!-- Textarea -->
<textarea rows="4" placeholder="Multiple lines..."></textarea>

<!-- Input with Addon -->
<div class="input-group">
    <input type="number" placeholder="Amount">
    <span class="input-group-addon">₹ INR</span>
</div>
```

---

### Form Actions
```html
<div class="form-actions">
    <button class="btn-secondary">Cancel</button>
    <button class="btn-primary">Submit</button>
</div>
```

---

## 🎴 Card Classes

### Auction Card (Browse Page)
```html
<div class="auction-card">
    <div class="auction-image">
        <img src="wheat.jpg" alt="Wheat">
        <span class="auction-status">Active</span>
        <span class="time-remaining">2h 30m left</span>
    </div>
    <div class="auction-content">
        <div class="crop-header">
            <h3 class="crop-title">Wheat</h3>
            <span class="location-badge">🌍 Jaipur</span>
        </div>
        
        <div class="price-section">
            <div class="price-item">
                <span class="price-label">Starting</span>
                <span class="price-value">₹4,000</span>
            </div>
            <div class="price-item highlight">
                <span class="price-label">Current</span>
                <span class="price-value">₹5,000</span>
            </div>
            <div class="price-item">
                <span class="price-label">Min Bid</span>
                <span class="price-value">₹500</span>
            </div>
        </div>

        <div class="stats-row">
            <span class="stat">📊 15 bids</span>
            <span class="stat">⏱️ 2h left</span>
        </div>

        <button class="btn-primary btn-full">View & Bid →</button>
    </div>
</div>
```

**Status Variants**:
```html
<span class="auction-status">Active</span>
<span class="auction-status ended">Ended</span>
```

**Time Remaining Variants**:
```html
<span class="time-remaining">2h 30m left</span>
<span class="time-remaining ending-soon">30m left</span>
```

---

### Bid Card (My Bids / Won Auctions)
```html
<div class="bid-card">
    <div class="bid-card-header">
        <h3 class="bid-card-title">Wheat Auction #2024</h3>
        <span class="badge badge-success">Won</span>
    </div>
    
    <div class="bid-card-body">
        <div class="bid-info">
            <span class="bid-label">Starting Price</span>
            <span class="bid-value">₹4,000</span>
        </div>
        <div class="bid-info">
            <span class="bid-label">Your Bid</span>
            <span class="bid-value primary">₹5,500</span>
        </div>
    </div>

    <div class="transaction-status">
        <span class="status-indicator completed"></span>
        <span class="status-text">Completed</span>
    </div>
</div>
```

**Badge Variants**:
```html
<span class="badge badge-success">Won</span>
<span class="badge badge-warning">Active</span>
<span class="badge badge-danger">Lost</span>
<span class="badge badge-info">Pending</span>
```

**Status Indicator Variants**:
```html
<span class="status-indicator pending"></span>
<span class="status-indicator completed"></span>
<span class="status-indicator failed"></span>
```

---

### Stat Card (Dashboard Metrics)
```html
<div class="stat-card">
    <h3 class="stat-card-number">24</h3>
    <p class="stat-card-label">Active Auctions</p>
</div>

<!-- Secondary Color -->
<div class="stat-card secondary">
    <h3 class="stat-card-number">₹45,000</h3>
    <p class="stat-card-label">Total Won</p>
</div>

<!-- Danger Color -->
<div class="stat-card danger">
    <h3 class="stat-card-number">8</h3>
    <p class="stat-card-label">Auctions Lost</p>
</div>

<!-- Warning Color -->
<div class="stat-card warning">
    <h3 class="stat-card-number">3</h3>
    <p class="stat-card-label">Active Bids</p>
</div>
```

---

## 🗂️ Modal & Dialog Classes

### Modal Dialog
```html
<div class="modal show">  <!-- Add 'show' class to display -->
    <div class="modal-content">
        <div class="modal-header">
            <h2>Place a Bid</h2>
            <button class="modal-close">✕</button>
        </div>
        
        <div class="modal-body">
            <p>Place your bid on this auction.</p>
            <!-- Form or content here -->
        </div>
        
        <div class="modal-footer">
            <button class="btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn-primary">Place Bid</button>
        </div>
    </div>
</div>

<!-- To show/hide modal -->
<script>
    document.querySelector('.modal').classList.add('show');     // Show
    document.querySelector('.modal').classList.remove('show');  // Hide
</script>
```

---

## 🔔 Notification Classes

### Toast Notification (Top-Right)
```html
<div class="notification-container">
    <!-- Success -->
    <div class="notification success">
        <span class="notification-icon">✓</span>
        <div class="notification-content">
            <p class="notification-message">Bid placed successfully!</p>
            <p class="notification-description">Your bid is now active</p>
        </div>
        <button class="notification-close">✕</button>
    </div>

    <!-- Error -->
    <div class="notification error">
        <span class="notification-icon">✕</span>
        <div class="notification-content">
            <p class="notification-message">Bid failed</p>
            <p class="notification-description">Insufficient balance</p>
        </div>
    </div>

    <!-- Warning -->
    <div class="notification warning">
        <span class="notification-icon">⚠️</span>
        <div class="notification-content">
            <p class="notification-message">Auction ending soon</p>
            <p class="notification-description">Only 30 minutes left to bid</p>
        </div>
    </div>

    <!-- Info -->
    <div class="notification info">
        <span class="notification-icon">ℹ️</span>
        <div class="notification-content">
            <p class="notification-message">New auction available</p>
            <p class="notification-description">Matching your interests</p>
        </div>
    </div>
</div>
```

---

### Alert Box (Page-Level)
```html
<!-- Success Alert -->
<div class="alert success">
    <span class="alert-icon">✓</span>
    <div class="alert-content">
        <p class="alert-title">Success!</p>
        <p class="alert-message">Your auction has been created successfully</p>
    </div>
</div>

<!-- Error Alert -->
<div class="alert error">
    <span class="alert-icon">✕</span>
    <div class="alert-content">
        <p class="alert-title">Error</p>
        <p class="alert-message">Failed to create auction. Please try again.</p>
    </div>
</div>

<!-- Warning Alert -->
<div class="alert warning">
    <span class="alert-icon">⚠️</span>
    <div class="alert-content">
        <p class="alert-title">Warning</p>
        <p class="alert-message">Your account balance is low</p>
    </div>
</div>

<!-- Info Alert -->
<div class="alert info">
    <span class="alert-icon">ℹ️</span>
    <div class="alert-content">
        <p class="alert-title">Information</p>
        <p class="alert-message">Auction will end in 2 hours</p>
    </div>
</div>
```

---

## 📑 Tab Navigation

### Tabs Container
```html
<div class="tabs-section">
    <button class="tab-button active">Browse Auctions</button>
    <button class="tab-button">My Bids</button>
    <button class="tab-button">Won Auctions</button>
</div>

<!-- Tab Content -->
<div class="tab-content active">
    <!-- Content for active tab -->
</div>
<div class="tab-content">
    <!-- Content for inactive tab -->
</div>

<script>
    // Make tabs functional with JavaScript
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active from all tabs and content
            document.querySelectorAll('.tab-button').forEach(b => 
                b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => 
                c.classList.remove('active'));
            
            // Add active to clicked tab
            e.target.classList.add('active');
            
            // Show corresponding content
            const index = Array.from(e.target.parentElement.children)
                .indexOf(e.target);
            document.querySelectorAll('.tab-content')[index]
                .classList.add('active');
        });
    });
</script>
```

---

## 🎁 Badge Classes

### Badge Variants
```html
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-danger">Rejected</span>
<span class="badge badge-info">Info</span>
```

---

## 📭 Empty State

```html
<div class="empty-state">
    <div class="empty-state-icon">📭</div>
    <h3 class="empty-state-title">No Active Bids</h3>
    <p class="empty-state-message">
        You haven't placed any bids yet. Browse auctions to get started!
    </p>
    <div class="empty-state-action">
        <a href="/browse" class="btn-primary">Browse Auctions</a>
    </div>
</div>
```

---

## ⏳ Loading State

### Skeleton Loader
```html
<!-- Skeleton Card -->
<div class="skeleton-card skeleton"></div>

<!-- Multiple Skeleton Cards -->
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
    <div class="skeleton-card skeleton"></div>
    <div class="skeleton-card skeleton"></div>
    <div class="skeleton-card skeleton"></div>
</div>

<!-- Skeleton Text -->
<div class="skeleton-text skeleton" style="width: 80%;"></div>
<div class="skeleton-text skeleton" style="width: 60%;"></div>
```

### Loading Spinner
```html
<div style="text-align: center; padding: 40px;">
    <div class="spinner"></div>
    <p style="margin-top: 20px; color: var(--text-muted);">Loading...</p>
</div>
```

---

## 🎨 Utility Classes

### Spacing Classes
```html
<!-- Margin Top -->
<div class="mt-10">Top margin 10px</div>
<div class="mt-20">Top margin 20px</div>
<div class="mt-30">Top margin 30px</div>
<div class="mt-40">Top margin 40px</div>

<!-- Margin Bottom -->
<div class="mb-10">Bottom margin 10px</div>
<div class="mb-20">Bottom margin 20px</div>
<div class="mb-30">Bottom margin 30px</div>
<div class="mb-40">Bottom margin 40px</div>

<!-- Padding -->
<div class="p-10">Padding 10px</div>
<div class="p-20">Padding 20px</div>
<div class="p-30">Padding 30px</div>
<div class="p-40">Padding 40px</div>
```

---

### Gap Classes (Flex/Grid)
```html
<div style="display: flex; gap: 20px;">
    <div class="gap-10">Item 1</div>  <!-- Alternative for gap -->
    <div class="gap-10">Item 2</div>
</div>
```

---

### Border Radius Classes
```html
<div class="rounded">Slightly rounded (8px)</div>
<div class="rounded-lg">Rounded (12px)</div>
<div class="rounded-xl">Very rounded (16px)</div>
```

---

### Shadow Classes
```html
<div class="shadow">Light shadow</div>
<div class="shadow-md">Medium shadow</div>
<div class="shadow-lg">Large shadow</div>
<div class="shadow-xl">Extra large shadow</div>
```

---

### Text & Display Classes
```html
<p class="text-center">Centered text</p>
<p class="text-right">Right-aligned text</p>

<div class="flex-center">Centered flex container</div>
<div class="flex-between">Space between flex items</div>

<div class="opacity-50">50% opacity</div>
<div class="opacity-75">75% opacity</div>

<a class="cursor-pointer">Clickable</a>
<div class="cursor-not-allowed">Not clickable</div>
```

---

## 🎬 Animation Classes

All animations are applied automatically. No need to add classes. They're triggered by:
- **Hover** on cards and buttons
- **Focus** on form inputs
- **Visibility** on page load (slideDown, fadeIn)
- **Status change** (pulse animation)

---

## 📐 Page Layouts

### Browse Auctions Container
```html
<div class="auction-browse-container">
    <div class="browse-header">
        <h1>Browse Active Auctions</h1>
        <p class="subtitle">Find and bid on fresh crops</p>
    </div>
    
    <div class="filters-section">
        <div class="filters-grid">
            <div class="filter-group">
                <label>Search</label>
                <input type="text" placeholder="Wheat, Rice...">
            </div>
        </div>
    </div>
    
    <div class="auctions-grid">
        <!-- Auction cards -->
    </div>
</div>
```

---

### Create Auction Container
```html
<div class="create-auction-container">
    <div class="form-header">
        <h1>Create New Auction</h1>
        <p>List your crop for bidding</p>
    </div>
    
    <div class="form-container">
        <!-- Form content -->
    </div>
</div>
```

---

## 🎯 Quick CSS Class Cheat Sheet

| Element | Class | Purpose |
|---------|-------|---------|
| Primary Button | `btn-primary` | Main actions |
| Secondary Button | `btn-secondary` | Cancel/Back |
| Danger Button | `btn-danger` | Delete/Risk |
| Full Width | `btn-full` | Stretch button |
| Form Container | `form-container` | Form wrapper |
| Form Group | `form-group` | Field + Label |
| Form Row | `form-row` | Two columns |
| Auction Card | `auction-card` | Browse cards |
| Bid Card | `bid-card` | Bid display |
| Stat Card | `stat-card` | Metrics |
| Modal | `modal` | Dialog box |
| Notification | `notification` | Toast msg |
| Alert | `alert` | Page alert |
| Badge | `badge` | Label/tag |
| Tab Button | `tab-button` | Navigation |
| Empty State | `empty-state` | No data msg |
| Skeleton | `skeleton` | Loading state |
| Spinner | `spinner` | Loading icon |

---

## 💡 Pro Tips

1. **Always use `.btn-full`** on mobile forms for touch-friendly buttons
2. **Combine `.form-row`** for better form layouts
3. **Use badges** for status indicators
4. **Add `.ending-soon`** to time-remaining for urgency
5. **Nest `.notification-container`** at end of body
6. **Keep `.modal.show`** for visibility toggle
7. **Use stat cards** for dashboard metrics
8. **Apply flex/grid utilities** for quick layouts

---

**Last Updated**: 2024
**CSS File**: `/static/css/bidding.css` (54KB)
**Status**: ✅ Production Ready
