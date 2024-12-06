import time
import keepasshttp
import sys
import pyperclip
import webbrowser
import json
import argparse

def matches_term(credential, term):
    """Check if credential matches search term in name or login"""
    term = term.lower()
    return term in credential.name.lower() or (credential.login and term in credential.login.lower())

def safe_copy(text):
    """Safely copy text to clipboard, handling None values"""
    if text is None:
        print("Warning: Nothing to copy (value is None)")
        return
    try:
        pyperclip.copy(str(text))
    except Exception as e:
        print(f"Warning: Could not copy to clipboard: {e}")

def safe_display(text):
    """Safely display text, handling None and encoding issues"""
    if text is None:
        return "N/A"
    try:
        return str(text)
    except:
        return "ERROR: Invalid encoding"

def save_credentials_list(credentials):
    """Save credentials list to file for debugging"""
    with open('credentials_list.txt', 'w', encoding='utf-8') as f:
        for i, cred in enumerate(credentials, 1):
            f.write(f"{i}. Name: {safe_display(cred.name)} | Login: {safe_display(cred.login)}\n")
    print("\nCredentials list saved to credentials_list.txt")

def display_credential_details(credential):
    """Display all available details for a credential"""
    print("\nCredential Details:")
    print("-" * 50)
    print(f"Name: {safe_display(credential.name)}")
    print(f"Login: {safe_display(credential.login)}")
    print(f"URL: {safe_display(credential.url)}")
    
    # Display any string fields if available
    if hasattr(credential, 'string_fields') and credential.string_fields:
        print("\nAdditional Fields:")
        for field in credential.string_fields:
            print(f"{field.get('Key', 'Unknown')}: {safe_display(field.get('Value', 'N/A'))}")
    print("-" * 50)

def show_and_select_credential(credentials):
    """Display credentials and let user select one"""
    # Show first 10 matches
    print(f"\nFound {len(credentials)} matches. Showing first 10:")
    for i, cred in enumerate(credentials[:10]):
        print(f"{i+1}. Name: {safe_display(cred.name)}")
        print(f"   Login: {safe_display(cred.login)}")
        print(f"   URL: {safe_display(cred.url)}")
        print()
    
    print("\nCommands:")
    print("1 or 1p = copy password")
    print("1n = copy name")
    print("1l = copy login")
    print("1u = copy URL")
    print("1uo = open URL in browser")
    
    try:
        choice = input("\nEnter selection: ").lower().strip()
        
        # Parse input
        if not choice:
            print("Invalid selection")
            sys.exit(1)
            
        # Extract number and command
        if choice.endswith('uo'):
            index = int(choice[:-2]) - 1
            command = 'uo'
        elif choice.endswith(('n', 'l', 'u')):
            index = int(choice[:-1]) - 1
            command = choice[-1]
        else:
            index = int(choice.rstrip('p')) - 1
            command = 'p'
            
        if index < 0 or index >= len(credentials):
            print("Invalid selection number")
            sys.exit(1)
            
        selected = credentials[index]
        
        # Display all details for selected credential
        display_credential_details(selected)
        
        # Handle command
        if command == 'n':
            print(f"Copying name for: {safe_display(selected.name)}")
            safe_copy(selected.name)
        elif command == 'l':
            print(f"Copying login for: {safe_display(selected.name)}")
            safe_copy(selected.login)
        elif command == 'u':
            print(f"Copying URL for: {safe_display(selected.name)}")
            safe_copy(selected.url)
        elif command == 'uo':
            print(f"Opening URL for: {safe_display(selected.name)}")
            if selected.url:
                webbrowser.open(selected.url)
            else:
                print("No URL available")
        else:  # password
            print(f"Copying password for: {safe_display(selected.name)}")
            safe_copy(selected.password)
            
    except (ValueError, IndexError):
        print("Invalid selection")
        sys.exit(1)

def try_search_with_case_variations(term):
    """Try searching with different case variations of the first character"""
    # First try original term
    print(f"\nTrying search with: {term}")
    credentials = keepasshttp.search(term)
    if credentials:
        return credentials

    # Try with first character lowercase
    if term[0].isupper():
        modified = term[0].lower() + term[1:]
        print(f"Trying search with: {modified}")
        credentials = keepasshttp.search(modified)
        if credentials:
            return credentials

    # Try with first character uppercase
    if term[0].islower():
        modified = term[0].upper() + term[1:]
        print(f"Trying search with: {modified}")
        credentials = keepasshttp.search(modified)
        if credentials:
            return credentials

    # Try using get() which uses Levenshtein Distance
    print(f"Trying fuzzy search with get()")
    credential = keepasshttp.get(term)
    if credential:
        return [credential]

    return None

def output_json(credential):
    """Output credential as JSON"""
    data = {
        'name': safe_display(credential.name),
        'login': safe_display(credential.login),
        'password': safe_display(credential.password),
        'url': safe_display(credential.url)
    }
    print(json.dumps(data))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KeePass credential retriever')
    parser.add_argument('search_term', help='Term to search for')
    parser.add_argument('--json', action='store_true', help='Output first match as JSON')
    args = parser.parse_args()
    
    # Try direct search with case variations and get()
    credentials = try_search_with_case_variations(args.search_term)
    
    # If still no results, try with list() approach
    if not credentials:
        print("No direct matches found, trying custom fuzzy search...")
        # Get all credentials and save to file
        all_credentials = keepasshttp.list()
        save_credentials_list(all_credentials)
        
        # Filter credentials
        credentials = [c for c in all_credentials if matches_term(c, args.search_term)]
        
        if not credentials:
            print("No credentials found")
            sys.exit(1)
    
    if args.json:
        # Output first match as JSON
        output_json(credentials[0])
    else:
        # Interactive mode
        show_and_select_credential(credentials)
