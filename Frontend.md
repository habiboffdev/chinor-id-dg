# Student Opportunity Management Platform - "Opportuni"
## Vanilla HTML/CSS/JavaScript Implementation

Build a comprehensive Student Opportunity Management Platform using **pure HTML, CSS, and JavaScript** - no npm modules, frameworks, or build tools required.

## 🏗️ Technical Requirements

**Core Technologies:**
- **HTML5** - Semantic markup with proper structure
- **CSS3** - Modern styling with CSS Grid, Flexbox, custom properties
- **Vanilla JavaScript** - ES6+ features, modules, async/await
- **Local Storage** - For data persistence (no backend required)
- **CSS-only components** - Custom UI components without libraries

**Project Structure:**
```
project/
├── index.html (Landing page)
├── dashboard.html (Student dashboard)
├── profile.html (Student profile)
├── opportunities.html (Browse opportunities)
├── event-details.html (Event details)
├── organization/
│   ├── dashboard.html (Organization dashboard)
│   ├── profile.html (Organization profile)
│   ├── students.html (Student management)
│   └── applications.html (Application management)
├── css/
│   ├── styles.css (Main styles)
│   ├── components.css (Reusable components)
│   └── responsive.css (Mobile-first responsive design)
├── js/
│   ├── main.js (Core functionality)
│   ├── data.js (Data management with localStorage)
│   ├── components.js (Reusable UI components)
│   └── utils.js (Utility functions)
└── assets/
    ├── images/
    └── icons/ (SVG icons)
```

## 📱 Pages & Features to Build

### 1. **Landing Page (index.html)**
- Hero section with CSS gradient background
- Features showcase with animated cards
- Benefits sections for different user types
- Call-to-action buttons with hover effects
- Fully responsive grid layout
- Smooth scrolling navigation

### 2. **Student Dashboard (dashboard.html)**
- Personal overview with CSS cards
- Application status tracking
- Quick stats display
- Recent opportunities section
- Navigation sidebar

### 3. **Student Profile (profile.html)**
- Editable profile form with validation
- Skills tags (add/remove functionality)
- Experience timeline
- Achievement badges
- Profile photo upload simulation

### 4. **Opportunities Browser (opportunities.html)**
- Grid/list view toggle
- Search functionality with live filtering
- Category filters (checkboxes/dropdowns)
- Sort options (date, relevance, deadline)
- Pagination with pure JavaScript
- Opportunity cards with hover effects

### 5. **Event Details (event-details.html)**
- Detailed event information display
- Application form with validation
- Requirements checklist
- Organization information sidebar
- Apply button with confirmation modal

### 6. **Organization Dashboard (organization/dashboard.html)**
Create a tabbed interface with 5 main sections:

**Overview Tab:**
- Statistics cards (applications, events, students)
- Charts using CSS-only bar/pie charts or Canvas API
- Quick action buttons

**Applications Tab:**
- Applications table with sortable columns
- Status badges (pending, accepted, rejected)
- Filter dropdown by status
- Bulk actions (select all, status update)
- Search functionality

**Students Tab:**
- Comprehensive student database table
- Advanced search (name, university, major, email)
- Multi-select checkboxes for bulk messaging
- Filter dropdowns (university, major, GPA range)
- Student profile links
- "Message Selected" and "Invite Students" buttons

**Events Tab:**
- Events management table
- Create new event modal (pure CSS/JS)
- Event status management
- Publish/unpublish buttons
- Delete confirmation modals
- Application count display

**Communications Tab:**
- Email template management system
- Pre-built template cards for:
  - Application confirmations
  - Interview invitations
  - Acceptance letters
  - Rejection letters
- Template editor with rich text simulation
- "Add New Template" functionality

### 7. **Organization Profile (organization/profile.html)**
Comprehensive profile management form:

**Basic Information:**
- Logo upload simulation with file input
- Organization name and type dropdown
- Description textarea with character counter
- Organization types: Education, Volunteering, Competition, etc.

**Contact Information:**
- Email and phone inputs with validation
- Form validation using JavaScript

**Location:**
- Country/city dropdowns or inputs
- Required field validation

**Social Media:**
- Website URL with validation
- Social media links (LinkedIn, Twitter, Facebook)
- URL format validation

### 8. **Student Detail Page (organization/students/student-detail.html)**
Detailed student view with tabs:

**Profile Tab:**
- Student information display
- Education, experience, projects sections
- Skills badges
- Activities list

**Applications Tab:**
- Application history table
- Status tracking
- Application details links

**Resume Tab:**
- Resume file simulation
- Download button
- Upload date display

**Notes Tab:**
- Organization notes about student
- Add new note functionality
- Timestamped entries

## 🎨 CSS Requirements

### Design System:
- **CSS Custom Properties** for consistent theming
- **CSS Grid & Flexbox** for layouts
- **Mobile-first responsive design**
- **CSS animations** for interactions
- **Custom form controls** (styled checkboxes, dropdowns)
- **CSS-only modals and dropdowns**
- **Loading states** with CSS animations
- **Toast notifications** using CSS animations + JavaScript

### UI Components to Build:
```css
/* Create these reusable components */
.btn { /* Button styles with variants */ }
.card { /* Card component with shadows */ }
.badge { /* Status badges */ }
.modal { /* Modal overlay and content */ }
.dropdown { /* Custom dropdown menus */ }
.table { /* Styled tables with sorting indicators */ }
.form-group { /* Form styling */ }
.tab-container { /* Tab interface */ }
.sidebar { /* Navigation sidebar */ }
.toast { /* Notification toasts */ }
```

### Responsive Breakpoints:
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

## 🚀 JavaScript Functionality

### Core Features:
1. **Data Management:**
   - localStorage for data persistence
   - JSON data structures for students, organizations, events
   - CRUD operations for all entities
   - Data validation functions

2. **Navigation:**
   - Single Page Application simulation with hash routing
   - Dynamic content loading
   - Breadcrumb navigation

3. **Search & Filtering:**
   - Live search functionality
   - Multiple filter combinations
   - Sort algorithms for tables
   - Pagination logic

4. **Form Handling:**
   - Form validation with custom rules
   - Dynamic form fields
   - File upload simulation
   - Multi-step forms

5. **Interactive Components:**
   - Tab switching
   - Modal dialogs
   - Dropdown menus
   - Collapsible sections
   - Drag and drop simulation

6. **Notifications:**
   - Toast notification system
   - Success/error messaging
   - Confirmation dialogs

### Data Structure Examples:
```javascript
// Sample data structures to implement
const student = {
  id: 'student_001',
  name: 'John Doe',
  email: 'john@university.edu',
  university: 'State University',
  major: 'Computer Science',
  gpa: 3.8,
  graduationYear: 2025,
  skills: ['JavaScript', 'Python', 'React'],
  applications: [],
  profile: { /* detailed profile data */ }
};

const organization = {
  id: 'org_001',
  name: 'Tech Corp',
  type: 'Corporation',
  description: '...',
  contact: { email, phone },
  location: { country, city },
  events: [],
  templates: []
};
```

## 🎯 Key Implementation Goals

1. **No External Dependencies** - Everything built from scratch
2. **Modern CSS** - Use latest CSS features (Grid, Custom Properties, etc.)
3. **ES6+ JavaScript** - Modern JavaScript features and best practices
4. **Responsive Design** - Works perfectly on all device sizes
5. **Accessible** - Proper ARIA labels, keyboard navigation
6. **Performance** - Optimized loading and smooth animations
7. **Code Organization** - Clean, modular, maintainable code structure

## 🔧 Advanced Features to Implement

- **CSV Export** functionality for data
- **Print-friendly** styles for reports
- **Keyboard shortcuts** for power users
- **Offline capability** with service workers (optional)
- **Data visualization** with Canvas API or CSS charts
- **Rich text editing** simulation for descriptions
- **Image compression** for profile photos
- **Bulk operations** for managing multiple items

This platform should serve as a comprehensive solution connecting students with opportunities while providing organizations powerful management tools - all built with vanilla web technologies for maximum compatibility and performance.