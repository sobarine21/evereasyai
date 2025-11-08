import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="WhoisJSON API Explorer",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

# Get API key from Supabase secrets
@st.cache_resource
def get_api_key():
    try:
        # Try to get from Streamlit secrets (Supabase secrets)
        return st.secrets["whoisjson"]["api_key"]
    except Exception as e:
        st.error(f"Error loading API key from secrets: {e}")
        return None

# API helper functions
def whois_lookup(domain, api_key):
    """Perform WHOIS lookup"""
    url = "https://whoisjson.com/api/v1/whois"
    params = {"domain": domain}
    headers = {"Authorization": f"Token={api_key}"}
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def nslookup(domain, api_key, record_type=None):
    """Perform DNS lookup"""
    url = "https://whoisjson.com/api/v1/nslookup"
    params = {"domain": domain}
    if record_type and record_type != "All Records":
        params["type"] = record_type
    headers = {"Authorization": f"Token={api_key}"}
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def ssl_cert_check(domain, api_key):
    """Check SSL certificate"""
    url = "https://whoisjson.com/api/v1/ssl"
    params = {"domain": domain}
    headers = {"Authorization": f"Token={api_key}"}
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# Helper function to display JSON results
def display_result(result, title):
    st.subheader(title)
    if result:
        # Create expandable JSON view
        with st.expander("📄 View Raw JSON", expanded=False):
            st.json(result)
        
        # Display formatted data
        if isinstance(result, dict):
            # Create a more organized display
            for key, value in result.items():
                if isinstance(value, dict):
                    st.markdown(f"**{key}:**")
                    for sub_key, sub_value in value.items():
                        st.markdown(f"  - *{sub_key}:* {sub_value}")
                elif isinstance(value, list):
                    st.markdown(f"**{key}:**")
                    for item in value:
                        st.markdown(f"  - {item}")
                else:
                    st.markdown(f"**{key}:** {value}")

# Main app
def main():
    st.title("🔍 WhoisJSON API Explorer")
    st.markdown("Explore WHOIS, DNS, and SSL certificate information for any domain")
    
    # Check if API key is available
    api_key = get_api_key()
    if not api_key:
        st.error("❌ API key not found in Supabase secrets. Please configure `whoisjson.api_key` in your secrets.")
        st.info("Add your API key to `.streamlit/secrets.toml`:\n```toml\n[whoisjson]\napi_key = \"your-api-key-here\"\n```")
        return
    
    st.success("✅ API key loaded successfully")
    
    # Sidebar for API selection
    st.sidebar.title("API Operations")
    operation = st.sidebar.radio(
        "Select Operation:",
        ["WHOIS Lookup", "DNS Lookup (nslookup)", "SSL Certificate Check", "Batch Operations"]
    )
    
    # Main content area
    if operation == "WHOIS Lookup":
        st.header("🌐 WHOIS Lookup")
        st.markdown("Get detailed domain registration information")
        
        domain = st.text_input("Enter Domain Name:", placeholder="example.com")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            lookup_btn = st.button("🔍 Lookup", type="primary", use_container_width=True)
        
        if lookup_btn and domain:
            with st.spinner(f"Fetching WHOIS data for {domain}..."):
                try:
                    result = whois_lookup(domain, api_key)
                    display_result(result, f"WHOIS Information for {domain}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"whois_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif operation == "DNS Lookup (nslookup)":
        st.header("🔎 DNS Lookup")
        st.markdown("Query DNS records for a domain")
        
        domain = st.text_input("Enter Domain Name:", placeholder="example.com")
        
        record_type = st.selectbox(
            "Select Record Type (optional):",
            ["All Records", "A", "MX", "TXT", "CNAME", "NS", "PTR", "AAAA", "SOA"]
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            lookup_btn = st.button("🔍 Lookup", type="primary", use_container_width=True)
        
        if lookup_btn and domain:
            with st.spinner(f"Fetching DNS records for {domain}..."):
                try:
                    result = nslookup(domain, api_key, record_type)
                    display_result(result, f"DNS Records for {domain}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"dns_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif operation == "SSL Certificate Check":
        st.header("🔒 SSL Certificate Check")
        st.markdown("Verify SSL/TLS certificate information")
        
        domain = st.text_input("Enter Domain Name:", placeholder="example.com")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            check_btn = st.button("🔍 Check", type="primary", use_container_width=True)
        
        if check_btn and domain:
            with st.spinner(f"Checking SSL certificate for {domain}..."):
                try:
                    result = ssl_cert_check(domain, api_key)
                    display_result(result, f"SSL Certificate for {domain}")
                    
                    # Show certificate validity
                    if isinstance(result, dict):
                        if 'valid_from' in result and 'valid_to' in result:
                            st.info(f"📅 Valid from: {result['valid_from']} to {result['valid_to']}")
                        elif 'notBefore' in result and 'notAfter' in result:
                            st.info(f"📅 Valid from: {result['notBefore']} to {result['notAfter']}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"ssl_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif operation == "Batch Operations":
        st.header("📦 Batch Operations")
        st.markdown("Perform lookups on multiple domains")
        
        domains_input = st.text_area(
            "Enter Domain Names (one per line):",
            placeholder="example.com\ngoogle.com\ngithub.com",
            height=150
        )
        
        batch_operation = st.selectbox(
            "Select Operation:",
            ["WHOIS Lookup", "DNS Lookup", "SSL Certificate Check"]
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            batch_btn = st.button("🚀 Run Batch", type="primary", use_container_width=True)
        
        if batch_btn and domains_input:
            domains = [d.strip() for d in domains_input.split('\n') if d.strip()]
            
            if not domains:
                st.warning("Please enter at least one domain")
                return
            
            st.info(f"Processing {len(domains)} domains...")
            
            results = {}
            progress_bar = st.progress(0)
            status_container = st.container()
            
            for idx, domain in enumerate(domains):
                try:
                    if batch_operation == "WHOIS Lookup":
                        results[domain] = whois_lookup(domain, api_key)
                    elif batch_operation == "DNS Lookup":
                        results[domain] = nslookup(domain, api_key)
                    elif batch_operation == "SSL Certificate Check":
                        results[domain] = ssl_cert_check(domain, api_key)
                    
                    with status_container:
                        st.success(f"✅ Completed: {domain}")
                except requests.exceptions.HTTPError as e:
                    with status_container:
                        st.error(f"❌ Failed: {domain} - HTTP {e.response.status_code}")
                    results[domain] = {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
                except Exception as e:
                    with status_container:
                        st.error(f"❌ Failed: {domain} - {str(e)}")
                    results[domain] = {"error": str(e)}
                
                progress_bar.progress((idx + 1) / len(domains))
            
            st.success(f"🎉 Batch operation completed! Processed {len(domains)} domains")
            
            # Display summary
            successful = sum(1 for r in results.values() if "error" not in r)
            failed = len(domains) - successful
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Successful", successful, delta=None)
            with col2:
                st.metric("Failed", failed, delta=None)
            
            # Display all results
            with st.expander("📊 View All Results", expanded=True):
                st.json(results)
            
            # Download button for batch results
            st.download_button(
                label="📥 Download Batch Results",
                data=json.dumps(results, indent=2),
                file_name=f"batch_{batch_operation.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("This app uses the WhoisJSON API to provide domain information, DNS records, and SSL certificate details.")
    st.sidebar.markdown("[WhoisJSON Documentation](https://whoisjson.com/documentation)")
    
    # API Info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Endpoints")
    st.sidebar.code("""
WHOIS: /api/v1/whois?domain=...
DNS:   /api/v1/nslookup?domain=...
SSL:   /api/v1/ssl?domain=...
    """)

if __name__ == "__main__":
    main()
