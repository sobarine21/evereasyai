import streamlit as st
from whoisjson import WhoisJsonClient
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

# Initialize client
@st.cache_resource
def get_client():
    api_key = get_api_key()
    if api_key:
        return WhoisJsonClient(api_key=api_key)
    return None

# Helper function to display JSON results
def display_result(result, title):
    st.subheader(title)
    if result:
        # Create expandable JSON view
        with st.expander("📄 View Raw JSON", expanded=False):
            st.json(result)
        
        # Display formatted data
        if isinstance(result, dict):
            cols = st.columns(2)
            idx = 0
            for key, value in result.items():
                with cols[idx % 2]:
                    if isinstance(value, (dict, list)):
                        st.markdown(f"**{key}:**")
                        st.json(value)
                    else:
                        st.markdown(f"**{key}:** {value}")
                idx += 1

# Main app
def main():
    st.title("🔍 WhoisJSON API Explorer")
    st.markdown("Explore WHOIS, DNS, and SSL certificate information for any domain")
    
    # Check if API key is available
    client = get_client()
    if not client:
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
                    result = client.whois(domain)
                    display_result(result, f"WHOIS Information for {domain}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"whois_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
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
                    if record_type == "All Records":
                        result = client.nslookup(domain)
                    else:
                        result = client.nslookup(domain, record_type=record_type)
                    
                    display_result(result, f"DNS Records for {domain}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"dns_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
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
                    result = client.ssl_cert_check(domain)
                    display_result(result, f"SSL Certificate for {domain}")
                    
                    # Show certificate validity
                    if isinstance(result, dict):
                        if 'valid_from' in result and 'valid_to' in result:
                            st.info(f"📅 Valid from: {result['valid_from']} to {result['valid_to']}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"ssl_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
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
            
            for idx, domain in enumerate(domains):
                try:
                    if batch_operation == "WHOIS Lookup":
                        results[domain] = client.whois(domain)
                    elif batch_operation == "DNS Lookup":
                        results[domain] = client.nslookup(domain)
                    elif batch_operation == "SSL Certificate Check":
                        results[domain] = client.ssl_cert_check(domain)
                    
                    st.success(f"✅ Completed: {domain}")
                except Exception as e:
                    st.error(f"❌ Failed: {domain} - {str(e)}")
                    results[domain] = {"error": str(e)}
                
                progress_bar.progress((idx + 1) / len(domains))
            
            st.success(f"🎉 Batch operation completed! Processed {len(domains)} domains")
            
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

if __name__ == "__main__":
    main()
