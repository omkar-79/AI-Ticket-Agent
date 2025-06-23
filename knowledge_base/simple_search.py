"""Simple knowledge base search using text file."""

import os
import re
from typing import List, Dict, Any, Optional


def load_knowledge_base() -> str:
    """Load the knowledge base text file."""
    kb_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base.txt")
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Knowledge base file not found at {kb_path}")
        return ""


def search_knowledge_base_simple(query: str, min_relevance_score: float = 0.8) -> List[Dict[str, Any]]:
    """
    Simple knowledge base search using text file.
    
    Args:
        query: Search query
        min_relevance_score: Minimum relevance score to consider a match (default: 0.8)
        
    Returns:
        List of matching solutions with relevance scores
    """
    kb_content = load_knowledge_base()
    if not kb_content:
        return []
    
    query_lower = query.lower()
    query_words = query_lower.split()
    
    # Extract sections and subsections
    sections = re.split(r'\n## ', kb_content)
    results = []
    
    for section in sections:
        if not section.strip():
            continue
            
        # Extract section title and content
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        section_title = lines[0].replace('#', '').strip()
        section_content = '\n'.join(lines[1:])
        
        # Calculate section relevance
        section_relevance = _calculate_relevance(query_words, section_title, section_content)
        
        # Extract subsections
        subsections = re.split(r'\n### ', section_content)
        for subsection in subsections:
            if not subsection.strip():
                continue
                
            # Extract subsection title and content
            sub_lines = subsection.strip().split('\n')
            if not sub_lines:
                continue
                
            subsection_title = sub_lines[0].strip()
            subsection_content = '\n'.join(sub_lines[1:])
            
            # Calculate subsection relevance
            subsection_relevance = _calculate_relevance(query_words, subsection_title, subsection_content)
            
            # Combined relevance (subsection gets higher weight)
            combined_relevance = (subsection_relevance * 0.7) + (section_relevance * 0.3)
            
            # Only include if relevance is above threshold
            if combined_relevance >= min_relevance_score:
                results.append({
                    "title": f"{section_title} - {subsection_title}",
                    "content": subsection_content,
                    "category": _categorize_section(section_title),
                    "relevance_score": combined_relevance,
                    "section": section_title,
                    "subsection": subsection_title
                })
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return results


def _calculate_relevance(query_words: List[str], title: str, content: str) -> float:
    """Calculate relevance score for a title and content."""
    relevance = 0.0
    
    # Convert to lowercase for comparison
    title_lower = title.lower()
    content_lower = content.lower()
    
    # Check for exact phrase matches (highest priority)
    query_phrase = ' '.join(query_words)
    if query_phrase in title_lower:
        relevance += 0.9
    if query_phrase in content_lower:
        relevance += 0.7
    
    # Check for word matches
    for word in query_words:
        if len(word) >= 3:  # Only meaningful words
            if word in title_lower:
                relevance += 0.3
            if word in content_lower:
                relevance += 0.1
    
    # Check for semantic matches (common IT terms)
    sound_terms = ['sound', 'audio', 'speaker', 'microphone', 'headphone', 'hear', 'hearing']
    network_terms = ['wifi', 'internet', 'vpn', 'network', 'connect', 'connection']
    hardware_terms = ['laptop', 'computer', 'monitor', 'printer', 'power', 'turn on']
    software_terms = ['software', 'application', 'install', 'crash', 'update']
    access_terms = ['password', 'login', 'account', 'lockout', 'reset']
    email_terms = ['email', 'outlook', 'send', 'receive', 'sync']
    
    # Check if query contains specific terms and content matches
    if any(term in query_words for term in sound_terms) and any(term in content_lower for term in sound_terms):
        relevance += 0.5
    if any(term in query_words for term in network_terms) and any(term in content_lower for term in network_terms):
        relevance += 0.5
    if any(term in query_words for term in hardware_terms) and any(term in content_lower for term in hardware_terms):
        relevance += 0.5
    if any(term in query_words for term in software_terms) and any(term in content_lower for term in software_terms):
        relevance += 0.5
    if any(term in query_words for term in access_terms) and any(term in content_lower for term in access_terms):
        relevance += 0.5
    if any(term in query_words for term in email_terms) and any(term in content_lower for term in email_terms):
        relevance += 0.5
    
    return min(relevance, 1.0)  # Cap at 1.0


def _categorize_section(section_title: str) -> str:
    """Categorize a section based on its title."""
    section_lower = section_title.lower()
    
    if 'sound' in section_lower or 'audio' in section_lower:
        return 'hardware'
    elif 'hardware' in section_lower:
        return 'hardware'
    elif 'network' in section_lower or 'wifi' in section_lower or 'vpn' in section_lower:
        return 'network'
    elif 'software' in section_lower or 'application' in section_lower:
        return 'software'
    elif 'access' in section_lower or 'password' in section_lower or 'login' in section_lower:
        return 'access'
    elif 'email' in section_lower:
        return 'email'
    else:
        return 'general'


def has_relevant_solution(query: str, min_relevance_score: float = 0.8) -> bool:
    """
    Check if there's a relevant solution for the query.
    
    Args:
        query: Search query
        min_relevance_score: Minimum relevance score to consider a match
        
    Returns:
        True if relevant solution found, False otherwise
    """
    results = search_knowledge_base_simple(query, min_relevance_score)
    return len(results) > 0 