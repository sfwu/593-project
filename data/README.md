# Database Files Directory

This directory contains all SQLite database files for the Academic Information Management System.

## 📂 File Organization

### **Main Database**
- `academic_management.db` - Main application database (development)

### **Test Databases** 
- `test_*.db` - Test databases (automatically created/cleaned during testing)
- These are ignored by git and cleaned up automatically

## 🚀 **Quick Start**

### **Initialize with Sample Data**
```bash
# Create database with sample students
python init_sample_data.py

# Clear and recreate database
python init_sample_data.py --clear

# Only clear database (no sample data)  
python init_sample_data.py --clear-only
```

### **Manual Database Management**
```bash
# Initialize database first (required)
python init_sample_data.py

# Then start services 
./start.sh

# Access database directly (if needed)
sqlite3 data/academic_management.db
```

## 📊 **Sample Data**

The `init_sample_data.py` script creates 5 sample students:

1. **John Doe** (CS001) - john.doe@university.edu
2. **Jane Smith** (CS002) - jane.smith@university.edu  
3. **Alice Johnson** (CS003) - alice.johnson@university.edu
4. **Bob Wilson** (CS004) - bob.wilson@university.edu
5. **Carol Brown** (CS005) - carol.brown@university.edu

## 🔧 **For Testing Course**

### **Benefits of This Structure:**
- ✅ **Consistent data** for all team members
- ✅ **Easy reset** to known state for testing
- ✅ **Sample data** for demonstration
- ✅ **Test isolation** (separate test DBs)
- ✅ **Git-friendly** organization

### **Testing Scenarios:**
```bash
# Test with fresh data
python init_sample_data.py --clear
python run_tests.py

# Test with existing data
python run_tests.py

# Manual testing with sample data
python init_sample_data.py
./start.sh
```

## 📝 **Database Schema**

### **Students Table**
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT, 
    email TEXT UNIQUE,
    student_id TEXT UNIQUE
);
```

## 🎯 **Git Strategy**

**Current Setup:**
- ✅ **Main database tracked** (committed to repository)
- ❌ **Test databases ignored** (not tracked)

**Database Git Workflow:**
```bash
# Initialize database with sample data
python init_sample_data.py

# Database is automatically tracked by git
git add data/academic_management.db
git commit -m "Add initialized database with sample data"

# Reset database (preserves git tracking)
python init_sample_data.py --clear
git add data/academic_management.db
git commit -m "Reset database to clean state"
```

This ensures **consistent starting state** for all team members!
