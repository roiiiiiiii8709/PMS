"""
Fix the approve_booking and decline_booking functions to accept 'pending_payment' status
"""

def fix_approval_functions():
    try:
        # Read the entire file
        file_path = 'app.py'
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Replace in approve_booking function
        original_approve = "if booking['status'] not in ['pending', None, ''] or \\\n           booking['status'] in ['confirmed', 'cancelled', 'entry', 'exited']:"
        new_approve = "if booking['status'] not in ['pending', 'pending_payment', None, ''] or \\\n           booking['status'] in ['confirmed', 'cancelled', 'entry', 'exited']:"
        
        # Replace in decline_booking function
        original_decline = "if booking['status'] not in ['pending', None, ''] or \\\n           booking['status'] in ['confirmed', 'cancelled', 'entry', 'exited']:"
        new_decline = "if booking['status'] not in ['pending', 'pending_payment', None, ''] or \\\n           booking['status'] in ['confirmed', 'cancelled', 'entry', 'exited']:"
        
        # Apply the replacements
        content = content.replace(original_approve, new_approve)
        content = content.replace(original_decline, new_decline)
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(content)
            
        print("Successfully updated approve_booking and decline_booking functions to accept 'pending_payment' status")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fix_approval_functions()
