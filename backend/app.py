from flask import Flask, request, jsonify
import sqlite3
import spacy
from datetime import datetime
from flask_cors import CORS


# Load English NLP model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS queries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 question TEXT,
                 intent TEXT,
                 timestamp DATETIME)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS responses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 intent TEXT,
                 response TEXT)''')
    
    # Sample data
    c.executemany("INSERT OR IGNORE INTO responses (intent, response) VALUES (?, ?)",
                  [
                ('admission', 'Admission requires: 1. 12th Marksheet 2. ID Proof 3. Application Form. Deadline: June 30.'),
                ('exam', 'The exams are scheduled in the first week of December.'),
                ('fee', 'Fee structure: Tuition - $2000/semester, Hostel - $500/month.'),
                ('scholarship', '🎓 Scholarships:\n1. Merit-based (above 90% in 12th)\n2. Sports Scholarships\n3. Economically Weaker Section\n\nApply before July 15. For details, contact scholarship@abcuniv.edu'),
                ('courses', '📚 Courses Offered:\n- B.Sc Computer Science\n- B.Com\n- B.E Mechanical, CSE, ECE\n- BA English, Economics\n- MBA, MCA\n\nVisit our website for detailed syllabus and eligibility.'),
                ('campus', '🏛️ Campus Facilities:\n- 24/7 Library\n- WiFi-enabled campus\n- Hostel for boys & girls\n- Canteen & medical facilities\n- Sports complex & gym\n\nCampus is eco-friendly with a vibrant student community.'),
                ('contact', '📞 Contact Us:\n- Email: enquiry@abcuniv.edu\n- Phone: +91-9876543210\n- Office Hours: Mon-Fri 9AM-5PM\n- Location: ABC University, Main Road, Chennai.\n\nWe are here to help!'),
                ('placement_info', '💼 Placements:\nOur placement cell assists students with internships and final placements.\nTop recruiters: TCS, Infosys, Wipro, Accenture.\nAvg Package: ₹4.5 LPA\n\nPlacement training begins from 3rd year.'),
                ('hostel_info', '🏠 Hostel Details:\n- Separate for boys and girls.\n- Triple sharing with attached bathrooms.\n- Mess facility (Veg/Non-Veg).\n- 24/7 security & WiFi.\n\nContact hostel@abcuniv.edu for room booking.'),
                ('library_info', '📖 Library Info:\n- Open 8AM-8PM (Mon-Sat)\n- 50,000+ books, e-resources, journals.\n- Reading rooms & discussion zones.\n\nLibrary card mandatory for borrowing books.'),
                ('transport', '🚌 Transport Facility:\n- College buses from major city routes.\n- Affordable yearly pass.\n- Tracking via student app.\n\nContact transport@abcuniv.edu for routes and pass details.'),
                ('timings', 'The college usually functions from 9:00 AM to 4:00 PM, Monday to Saturday.'),
                ('semester_start', 'The next semester is expected to begin in the first week of July or January, depending on the academic calendar.'),
                ('bonafide_certificate', 'You can apply for a bonafide certificate in the college office by filling out a form and submitting a copy of your ID card.'),
                ('transfer_certificate', 'To get a transfer certificate (TC): 1. Submit written application 2. Attach ID proof 3. Get department clearances 4. Processing takes 3-5 working days.'),
                ('location', 'The administrative office is located on the ground floor near the main entrance of the college.'),
                ('curriculum', 'Subjects include Operating Systems, Data Mining, Python Programming, Mobile App Development, and Project Work.'),
                ('academic_calendar', 'The academic calendar is available on the college notice board and also on the official college website.'),
                ('exams', 'There are two internal exams and one model exam before the semester-end examination.'),
                ('results', 'Results are usually published within 30–45 days after the last exam.'),
                ('attendance', 'A minimum of 75% attendance is required to appear for semester exams.'),
                ('passing_marks', 'Students must score at least 40% in each subject to pass.'),
                ('unit_test', 'The next unit test is scheduled as per the timetable. Please check the latest circular or department notice board.'),
                ('revaluation', 'You can apply through the exam cell by filling out the revaluation form and paying the required fee.'),
                ('canteen_facilities', 'The canteen is located near the auditorium block, open from 9 AM to 4 PM.'),
                ('ncc_nss', 'You can join by registering your name with the respective coordinator during the enrollment period.'),
                ('sports', 'Our college has facilities for cricket, volleyball, badminton, and indoor games.'),
                ('events', 'The next cultural event is usually held during January (Pongal Fest) or April (Annual Day).'),
                ('participation', 'You can give your name to the event coordinator or your class in-charge.'),
                ('annual_day', 'Annual Day includes dance, drama, prize distribution, speeches, and guest performances.'),
                ('dress_code', 'Students are usually asked to wear traditional or formal attire.'),
                ('visitors', 'Only invited guests and parents are allowed. Outsiders are generally not permitted unless approved.'),
                ('placement', 'You can register through the placement cell or by filling out the online Google form shared in class groups.'),
                ('internship', 'Most courses require a minimum 15-day internship in the final year.'),
                ('submission', 'Submit your report in hard copy to your department and upload a soft copy on the portal (if applicable).'),
                ('concession', 'Yes, based on eligibility, apply through the scholarship section of the admin office.'),
                ('marksheet', 'Consolidated mark sheets can be collected from the exam cell after announcement of results.')
                   ])
    
    conn.commit()
    conn.close()

init_db()

# NLP Intent Recognition
def detect_intent(text):
    doc = nlp(text.lower())
    text_lower = text.lower()
    # Expanded intent detection
   
    if any(token.text in ['timings', 'working hours', 'open', 'close', 'hour', 'time'] for token in doc):
        return 'timings'
    elif any(token.text in ['semester', 'start', 'begin', 'commence', 'session'] for token in doc):
        return 'semester_start'
    elif any(token.text in ['transfer', 'tc', 'leaving certificate', 'transfer certificate'] for token in doc):
        return 'transfer_certificate'
    elif any(token.text in ['certificate', 'bonafide', 'bonafide certificate', 'study certificate'] for token in doc):
        return 'bonafide_certificate'
    elif any(token.text in ['location', 'where', 'located', 'office', 'find'] for token in doc):
        return 'location'
    elif any(token.text in ['subject', 'curriculum', 'syllabus', 'course content'] for token in doc):
        return 'curriculum'
    elif any(token.text in ['calendar', 'schedule', 'academic calendar'] for token in doc):
        return 'academic_calendar'
    elif any(token.text in ['internal exam', 'model exam', 'prelim'] for token in doc):
        return 'exams'
    elif any(token.text in ['result', 'publish', 'declare', 'marks', 'grade'] for token in doc):
        return 'results'
    elif any(token.text in ['attendance', 'present', 'absent', 'percentage'] for token in doc):
        return 'attendance'
    elif any(token.text in ['pass', 'marks', 'minimum', 'cutoff'] for token in doc):
        return 'passing_marks'
    elif any(token.text in ['unit test', 'assessment', 'quiz'] for token in doc):
        return 'unit_test'
    elif any(token.text in ['revaluation', 'recheck', 'reverify'] for token in doc):
        return 'revaluation'
    elif any(token.text in ['canteen', 'food', 'eat', 'mess'] for token in doc):
        return 'canteen_facilities'
    elif any(token.text in ['ncc', 'nss', 'join', 'national cadet corps'] for token in doc):
        return 'ncc_nss'
    elif any(token.text in ['sports', 'games', 'play', 'athletic'] for token in doc):
        return 'sports'
    elif any(token.text in ['event', 'cultural', 'program', 'function'] for token in doc):
        return 'events'
    elif any(token.text in ['participate', 'competition', 'contest'] for token in doc):
        return 'participation'
    elif any(token.text in ['annual day', 'annual function'] for token in doc):
        return 'annual_day'
    # elif any(token.text in ['dress code', 'attire', 'uniform'] for token in doc):
    #     return 'dress_code'
    elif any(phrase in text_lower for phrase in ['dress code', 'dresscode', 'what to wear', 'college uniform']):
        return 'dress_code'
    elif any(token.text in ['visitor', 'outsider', 'parent', 'guest'] for token in doc):
        return 'visitors'
    elif any(token.text in ['internship', 'training', 'industrial'] for token in doc):
        return 'internship'
    elif any(token.text in ['submit', 'report', 'project', 'assignment'] for token in doc):
        return 'submission'
    elif any(token.text in ['concession', 'discount', 'waiver'] for token in doc):
        return 'concession'
    elif any(token.text in ['marksheet', 'consolidated', 'degree', 'certificate'] for token in doc):
        return 'marksheet'
    elif any(token.text in ['admission', 'apply', 'admit', 'eligibility', 'enroll', 'enrollment'] for token in doc):
        return 'admission'
    elif any(token.text in ['exam', 'test', 'schedule', 'midterm', 'final','exams'] for token in doc):
        return 'exam'
    elif any(token.text in ['fee', 'payment', 'cost', 'tuition', 'hostel fee', 'fees'] for token in doc):
        return 'fee'
    elif any(token.text in ['scholarship', 'financial aid', 'grant', 'funding', 'education loan'] for token in doc):
        return 'scholarship'
    elif any(token.text in ['course', 'program', 'degree', 'bsc', 'bcom', 'mba', 'bca', 'engineering'] for token in doc):
        return 'courses'
    elif any(token.text in ['campus', 'facility', 'infrastructure', 'building', 'ground'] for token in doc):
        return 'campus'
    elif any(token.text in ['contact', 'email', 'phone', 'address', 'reach', 'number'] for token in doc):
        return 'contact'
    elif any(token.text in ['placement', 'job', 'recruitment', 'career', 'company', 'recruiter'] for token in doc):
        return 'placement_info'
    elif any(token.text in ['hostel', 'accommodation', 'room', 'stay', 'lodging','hostel facilities'] for token in doc):
        return 'hostel_info'
    elif any(token.text in ['library', 'book', 'journal', 'study', 'reference'] for token in doc):
        return 'library_info'
    elif any(token.text in ['transport', 'bus', 'vehicle', 'commute', 'travel'] for token in doc):
        return 'transport'
    else:
        return 'general'

# API Endpoint for Chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    
    # Log the query
    intent = detect_intent(user_message)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO queries (question, intent, timestamp) VALUES (?, ?, ?)",
              (user_message, intent, timestamp))
    
    # Get appropriate response
    c.execute("SELECT response FROM responses WHERE intent=?", (intent,))
    result = c.fetchone()
    # response = result[0] if result else "I'm not sure I understand. Can you rephrase?"
    if result:
        response = result[0]
    else:
        # Enhanced fallback response with contact support suggestion
       response = """❓ I couldn't find specific information for your query.\n\nFor detailed assistance with this topic, please contact our support team:\n\n📞 Contact Support:\n• Email: enquiry@abcuniv.edu\n• Phone: +91-9876543210\n• Office Hours: Mon-Fri 9AM-5PM"""
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'response': response,
        'intent': intent
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)