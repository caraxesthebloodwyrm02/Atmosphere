#!/usr/bin/env python3
"""
Universal Content Transformer & Monetization Pipeline
Enhanced with Niche Analysis and Smart Monetization
"""

import time
from functools import wraps
from typing import Callable, Any, Optional, Union
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
from docx import Document
import csv
from enum import Enum, auto
import re
import logging
import os
import asyncio
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field

# Import business initiative workflow
from app.agents import BusinessInitiativeWorkflow, TriageSchema
@dataclass
@dataclass
class BusinessInitiativeConfig:
    """Configuration for Business Initiative Workflow"""
    default_models: Dict[str, str] = field(default_factory=lambda: {
        'triage': 'gpt-4',
        'launch_helper': 'gpt-4',
        'get_data': 'gpt-4'
    })
    enabled: bool = True
    max_concurrent_workflows: int = 5
    default_timeout: int = 300  # seconds
    enable_web_search: bool = True
    web_search_provider: str = 'duckduckgo'  # or 'google', 'bing', etc.


@dataclass
class PipelineConfig:
    """Configuration for the MonetizationPipeline"""
    output_dir: Path = field(default_factory=lambda: Path("monetization_outputs"))
    debug: bool = False
    log_level: str = "INFO"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: List[str] = field(default_factory=lambda: [
        'youtube', 'article', 'newsletter', 'social_media', 'business_initiative'
    ])
    enable_progress_logging: bool = True
    sanitize_input: bool = True
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    enable_benchmarking: bool = False
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    
    # Supported output formats
    supported_formats: List[str] = field(default_factory=lambda: ['youtube', 'article', 'newsletter', 'social_media'])
    
    # Progress reporting
    progress_callback: Optional[Callable[[str, float], None]] = None
    
    # SEO and quality settings
    enable_seo_optimization: bool = True
    min_content_length: int = 300  # minimum words for good SEO
    
    # Business initiative workflow settings
    business_initiative: BusinessInitiativeConfig = field(default_factory=BusinessInitiativeConfig)
    
    @classmethod
    def from_env(cls) -> 'PipelineConfig':
        """Create config from environment variables"""
        return cls(
            output_dir=Path(os.getenv('PIPELINE_OUTPUT_DIR', 'monetization_outputs')),
            debug=os.getenv('PIPELINE_DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('PIPELINE_LOG_LEVEL', 'INFO'),
            max_file_size=int(os.getenv('PIPELINE_MAX_FILE_SIZE', '10485760')),  # 10MB default
            enable_progress_logging=os.getenv('PIPELINE_PROGRESS_LOGGING', 'true').lower() == 'true',
            sanitize_input=os.getenv('PIPELINE_SANITIZE_INPUT', 'true').lower() == 'true',
            enable_performance_monitoring=os.getenv('PIPELINE_PERFORMANCE_MONITORING', 'true').lower() == 'true',
            enable_benchmarking=os.getenv('PIPELINE_BENCHMARKING', 'false').lower() == 'true',
            max_retries=int(os.getenv('PIPELINE_MAX_RETRIES', '3')),
            retry_delay=float(os.getenv('PIPELINE_RETRY_DELAY', '1.0')),
            enable_seo_optimization=os.getenv('PIPELINE_SEO_OPTIMIZATION', 'true').lower() == 'true',
            min_content_length=int(os.getenv('PIPELINE_MIN_CONTENT_LENGTH', '300'))
        )

class PipelineResult:
    """Result of a pipeline operation with partial success support"""
    def __init__(self):
        self.successes: Dict[str, str] = {}
        self.failures: Dict[str, str] = {}
        self.warnings: List[str] = []
        # Performance metrics
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.total_time: Optional[float] = None
        self.operation_times: Dict[str, float] = {}

    def start_timing(self):
        """Start timing the pipeline operation"""
        self.start_time = time.time()
    
    def end_timing(self):
        """End timing and calculate total duration"""
        self.end_time = time.time()
        if self.start_time:
            self.total_time = self.end_time - self.start_time
    
    def record_operation_time(self, operation: str, duration: float):
        """Record the time taken for a specific operation"""
        self.operation_times[operation] = duration

    def add_success(self, format_name: str, file_path: str):
        self.successes[format_name] = file_path

    def add_failure(self, format_name: str, error: str):
        self.failures[format_name] = error

    def add_warning(self, message: str):
        self.warnings.append(message)

    def is_complete_success(self) -> bool:
        return len(self.failures) == 0 and len(self.successes) > 0

    def has_partial_success(self) -> bool:
        return len(self.successes) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'successes': self.successes,
            'failures': self.failures,
            'warnings': self.warnings,
            'complete_success': self.is_complete_success(),
            'partial_success': self.has_partial_success(),
            'performance': {
                'total_time': self.total_time,
                'operation_times': self.operation_times,
                'start_time': self.start_time,
                'end_time': self.end_time
            }
        }

def timed_operation(operation_name: str = None):
    """Decorator to time pipeline operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.config.enable_performance_monitoring:
                return func(self, *args, **kwargs)
            
            name = operation_name or f"{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(self, *args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                
                if hasattr(self, 'current_result') and self.current_result:
                    self.current_result.record_operation_time(name, duration)
                
                if self.config.enable_benchmarking:
                    self.logger.debug(f"⏱️ Operation '{name}' completed in {duration:.3f}s")
                
                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                self.logger.warning(f"❌ Operation '{name}' failed after {duration:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

class _TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, pipeline, operation_name: str):
        self.pipeline = pipeline
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            if hasattr(self.pipeline, 'logger'):
                self.pipeline.logger.debug(f"⏱️ Operation '{self.operation_name}' took {duration:.3f}s")


def retry_on_failure(max_retries: int = None, delay: float = None, exceptions: tuple = (Exception,)):
    """Decorator to retry operations on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = max_retries or self.config.max_retries
            retry_delay = delay or self.config.retry_delay
            
            last_exception = None
            for attempt in range(retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        self.logger.warning(f"⚠️ Operation '{func.__name__}' failed (attempt {attempt + 1}/{retries + 1}): {str(e)}. Retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        self.logger.error(f"❌ Operation '{func.__name__}' failed after {retries + 1} attempts")
                        raise last_exception
        return wrapper
    return decorator

class ContentType(Enum):
    TUTORIAL = "tutorial"
    LIST = "list"
    REVIEW = "review"
    ANALYSIS = "analysis"
    STORY = "story"
    GUIDE = "guide"
    BUSINESS_INITIATIVE = "business_initiative"

@dataclass
class ContentAnalysis:
    """Enhanced content analysis with monetization insights"""
    content_type: ContentType
    sentiment: str
    word_count: int
    monetization_potential: float  # 0-100 scale
    semantic_fields: Dict[str, float]
    temporal_context: Dict[str, Any]
    recommended_platforms: List[str]
    competition_level: str

class NicheMicroscope:
    """Enhanced niche analysis with semantic understanding"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.semantic_fields = {
            'technology': ['AI', 'blockchain', 'IoT', 'machine learning', 'automation'],
            'lifestyle': ['minimalism', 'productivity', 'wellness', 'mindfulness'],
            'business': ['startup', 'entrepreneurship', 'freelancing', 'remote work']
        }
    
    def analyze(self, text: str) -> ContentAnalysis:
        """Comprehensive content analysis"""
        content_type = self._categorize_content(text)
        sentiment = self._detect_sentiment(text)
        semantic_fields = self._analyze_semantics(text)
        
        return ContentAnalysis(
            content_type=content_type,
            sentiment=sentiment,
            word_count=len(text.split()),
            monetization_potential=self._calculate_monetization_potential(text, content_type),
            semantic_fields=semantic_fields,
            temporal_context=self._analyze_temporal_context(text),
            recommended_platforms=self._recommend_platforms(content_type, semantic_fields),
            competition_level=self._assess_competition(text)
        )
    
    def _categorize_content(self, text: str) -> ContentType:
        text_lower = text.lower()
        if any(word in text_lower for word in ["how to", "tutorial", "guide", "step"]):
            return ContentType.TUTORIAL
        elif any(word in text_lower for word in ["list", "top", "best", "worst"]):
            return ContentType.LIST
        elif any(word in text_lower for word in ["review", "opinion", "thoughts on"]):
            return ContentType.REVIEW
        elif re.search(r'\d+.*\d+', text) and any(word in text_lower for word in ["data", "metric", "score"]):
            return ContentType.ANALYSIS
        elif any(word in text_lower for word in ["story", "day", "went", "experience"]):
            return ContentType.STORY
        return ContentType.GUIDE
    
    def _detect_sentiment(self, text: str) -> str:
        # Simple sentiment analysis - can be enhanced with NLTK or similar
        positive = len(re.findall(r'\b(good|great|amazing|love|best|happy|success)\b', text.lower()))
        negative = len(re.findall(r'\b(bad|terrible|hate|worst|sad|fail)\b', text.lower()))
        return "positive" if positive > negative else "negative" if negative > positive else "neutral"
    
    def _analyze_semantics(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        scores = {field: sum(1 for kw in keywords if kw.lower() in text_lower)
                 for field, keywords in self.semantic_fields.items()}
        total = sum(scores.values()) or 1
        return {k: v/total for k, v in scores.items()}
    
    def _analyze_temporal_context(self, text: str) -> Dict[str, Any]:
        return {
            'is_time_sensitive': bool(re.search(r'\b(202[3-9]|20[3-9]\d)\b', text)),
            'keywords': [word for word in ['new', 'trending', 'now'] if word in text.lower()],
            'seasonal': self._detect_seasonal(text)
        }
    
    def _detect_seasonal(self, text: str) -> Optional[str]:
        seasons = {
            'winter': ['winter', 'christmas', 'new year', 'holiday'],
            'spring': ['spring', 'easter', 'tax', 'graduation'],
            'summer': ['summer', 'vacation', 'beach', 'travel'],
            'fall': ['fall', 'autumn', 'halloween', 'thanksgiving']
        }
        text_lower = text.lower()
        for season, terms in seasons.items():
            if any(term in text_lower for term in terms):
                return season
        return None
    
    def _calculate_monetization_potential(self, text: str, content_type: ContentType) -> float:
        # Base score by content type
        base_scores = {
            ContentType.TUTORIAL: 80,
            ContentType.REVIEW: 75,
            ContentType.ANALYSIS: 85,
            ContentType.LIST: 70,
            ContentType.STORY: 60,
            ContentType.GUIDE: 75
        }
        
        score = base_scores.get(content_type, 50)
        
        # Adjust based on content characteristics
        if len(text) > 500:
            score += 10  # Longer content generally performs better
        if any(word in text.lower() for word in ['how to', 'tutorial', 'guide']):
            score += 5  # Instructional content has high value
        if any(word in text.lower() for word in ['best', 'vs', 'review']):
            score += 7  # Comparison/decision-making content
        
        return min(100, score)  # Cap at 100
    
    def _recommend_platforms(self, content_type: ContentType, semantic_fields: Dict[str, float]) -> List[str]:
        platforms = []
        
        if content_type in [ContentType.TUTORIAL, ContentType.GUIDE]:
            platforms.extend(['YouTube', 'Medium', 'Personal Blog'])
        if content_type == ContentType.REVIEW:
            platforms.extend(['YouTube', 'Amazon Associates', 'Affiliate Blogs'])
        if content_type == ContentType.ANALYSIS:
            platforms.extend(['Substack', 'LinkedIn', 'Industry Reports'])
        if content_type == ContentType.LIST:
            platforms.extend(['Listicle Sites', 'Social Media', 'Email Newsletters'])
        
        # Add platforms based on semantic fields
        if semantic_fields.get('technology', 0) > 0.3:
            platforms.extend(['Dev.to', 'Hacker News', 'GitHub'])
        if semantic_fields.get('business', 0) > 0.3:
            platforms.extend(['LinkedIn', 'Twitter', 'Industry Forums'])
        
        return list(dict.fromkeys(platforms))  # Remove duplicates while preserving order
    
    def _assess_competition(self, text: str) -> str:
        # This is a simplified version - in production, you'd want to:
        # 1. Search for similar content
        # 2. Analyze top results
        # 3. Calculate competition metrics
        
        # For now, we'll use a simple heuristic based on content length and keywords
        word_count = len(text.split())
        has_popular_keywords = any(word in text.lower() for word in 
                                 ['how to', 'best', 'review', 'vs', 'tutorial'])
        
        if word_count > 1000 and has_popular_keywords:
            return "high"
        elif word_count > 500 or has_popular_keywords:
            return "medium"
        return "low"

class MonetizationPipeline:
    """
    Enhanced Monetization Pipeline with Niche Analysis
    Transforms raw input into structured, monetizable content with smart formatting.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.config.output_dir.mkdir(exist_ok=True)
        self.microscope = NicheMicroscope(debug=self.config.debug)

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, self.config.log_level))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Content transformation strategies
        self.transformers = {
            'youtube': self._transform_to_youtube,
            'article': self._transform_to_article,
            'newsletter': self._transform_to_newsletter,
            'social_media': self._transform_for_social,
            'business_initiative': self._transform_business_initiative
        }
        
        # Initialize business initiative workflow if enabled
        self.business_initiative_workflow = None
        if self.config.business_initiative.enabled:
            self._init_business_initiative_workflow()
    
    def _time_operation(self, operation_name: str):
        """Context manager for timing operations"""
        return _TimingContext(self, operation_name)
    
    def _init_business_initiative_workflow(self):
        """Initialize the business initiative workflow"""
        try:
            # In a real implementation, you would pass the actual assistant instance
            # For now, we'll pass None and the workflow will use default settings
            self.business_initiative_workflow = BusinessInitiativeWorkflow(
                assistant=None  # Replace with actual assistant instance
            )
            self.logger.info("Business Initiative Workflow initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Initiative Workflow: {str(e)}")
            self.business_initiative_workflow = None
    
    def process(self, text: str, output_formats: List[str] = None) -> PipelineResult:
        """
        Process input text and generate monetizable outputs with partial success support.
        
        Args:
            text: Input content to process (must be a non-empty string)
            output_formats: List of formats to generate (default: auto-detect)
            
        Returns:
            PipelineResult with successes, failures, and warnings
        """
        result = PipelineResult()
        self.current_result = result  # For decorator access
        
        # Start timing
        result.start_timing()
        if self.config.progress_callback:
            self.config.progress_callback("Starting pipeline", 0.0)
        
        try:
            # Input validation and sanitization
            text = self._validate_and_sanitize_input(text)
            if self.config.progress_callback:
                self.config.progress_callback("Input validation complete", 0.1)
            
            # Analyze content
            analysis = self._analyze_content(text)
            if self.config.progress_callback:
                self.config.progress_callback("Content analysis complete", 0.3)
            
            # Determine output formats
            if not output_formats:
                output_formats = self._select_formats(analysis)
            
            # Validate formats and generate outputs
            self._generate_outputs(text, analysis, output_formats, result)
            
            if self.config.progress_callback:
                self.config.progress_callback("Output generation complete", 1.0)
                
        except Exception as e:
            result.add_failure("pipeline_error", f"Pipeline failed: {str(e)}")
            self.logger.error(f"❌ Pipeline failed: {str(e)}")
        finally:
            # End timing
            result.end_timing()
            self.current_result = None
            
            if self.config.enable_performance_monitoring and result.total_time:
                self.logger.info(f"⏱️ Pipeline completed in {result.total_time:.3f}s")
        
        return result
    
    @timed_operation("content_analysis")
    def _analyze_content(self, text: str) -> ContentAnalysis:
        """Analyze content with timing"""
        with self._time_operation("content_analysis"):
            # Try to detect if this is a business initiative request
            is_business_initiative = any([
                keyword in text.lower() 
                for keyword in [
                    'launch', 'initiative', 'business plan', 'strategy',
                    'project', 'product launch', 'market entry'
                ]
            ])
            
            analysis = self.microscope.analyze(text)
            
            # Override content type if this looks like a business initiative
            if is_business_initiative:
                analysis.content_type = ContentType.BUSINESS_INITIATIVE
                
            return analysis
    
    @retry_on_failure()
    @timed_operation()
    def _generate_outputs(self, text: str, analysis: ContentAnalysis, 
                         output_formats: List[str], result: PipelineResult):
        """Generate outputs with retry logic and timing"""
        # Validate requested formats
        valid_formats = [fmt for fmt in output_formats if fmt in self.config.supported_formats]
        invalid_formats = [fmt for fmt in output_formats if fmt not in self.config.supported_formats]
        
        if invalid_formats:
            result.add_warning(f"Unsupported formats ignored: {', '.join(invalid_formats)}")
        
        total_formats = len(valid_formats)
        for i, fmt in enumerate(valid_formats):
            try:
                if self.config.progress_callback:
                    progress = 0.3 + (0.7 * (i / max(total_formats, 1)))
                    self.config.progress_callback(f"Generating {fmt}", progress)
                
                file_path = self.transformers[fmt](text, analysis)
                result.add_success(fmt, file_path)
                
                if self.config.enable_progress_logging:
                    self.logger.info(f"✅ Generated {fmt}: {file_path}")
                    
            except Exception as e:
                result.add_failure(fmt, f"Failed to generate {fmt}: {str(e)}")
                self.logger.warning(f"❌ Failed to generate {fmt}: {str(e)}")
        
        if result.has_partial_success():
            if result.is_complete_success():
                self.logger.info(f"🎉 Pipeline completed successfully. Generated {len(result.successes)} formats.")
            else:
                self.logger.warning(f"⚠️ Pipeline completed with partial success. {len(result.successes)} successful, {len(result.failures)} failed.")
    
    def _validate_and_sanitize_input(self, text: str) -> str:
        """Validate and sanitize input text"""
        if not isinstance(text, str):
            raise ValueError(f"Expected string, got {type(text).__name__}")
            
        text = text.strip()
        if not text:
            raise ValueError("Input text cannot be empty")
        
        # Check file size limit (rough estimate: 2 bytes per character for UTF-8)
        if len(text.encode('utf-8')) > self.config.max_file_size:
            raise ValueError(f"Input text too large. Maximum size: {self.config.max_file_size} bytes")
        
        # Basic sanitization if enabled
        if self.config.sanitize_input:
            # Remove potentially dangerous patterns
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
            text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _select_formats(self, analysis: ContentAnalysis) -> List[str]:
        """Select appropriate output formats based on content analysis"""
        formats = []
        
        # Handle business initiative content type
        if analysis.content_type == ContentType.BUSINESS_INITIATIVE:
            if self.config.business_initiative.enabled:
                return ['business_initiative']
            else:
                self.logger.warning(
                    "Business Initiative content detected but the workflow is disabled. "
                    "Falling back to default formats."
                )
        
        # Basic format selection based on content type
        if analysis.content_type in [ContentType.TUTORIAL, ContentType.GUIDE]:
            formats.extend(['youtube', 'article'])
        elif analysis.content_type == ContentType.LIST:
            formats.extend(['article', 'social_media'])
        elif analysis.content_type == ContentType.REVIEW:
            formats.extend(['article', 'social_media'])
        else:
            formats.append('article')
            
        # Add newsletter for longer content
        if analysis.word_count > 500:
            formats.append('newsletter')
            
        return list(set(formats))  # Remove duplicates
    
    def _transform_to_youtube(self, text: str, analysis: ContentAnalysis) -> str:
        """Transform content into a YouTube script"""
        output_file = self.config.output_dir / f"youtube_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Generate title based on content type and sentiment (without emojis)
        title = self._generate_title(analysis, use_emoji=False)
        
        # Generate script sections with text-based emojis
        script = f"""# {title}

[INTRO]
{self._generate_intro(analysis).replace('🔥', '[HOT] ').replace('⚠️', '[WARNING] ')}

[MAIN CONTENT]
{self._structure_content(text, analysis)}

[CONCLUSION]
{self._generate_conclusion(analysis).replace('🔥', '[HOT] ').replace('⚠️', '[WARNING] ')}

[DESCRIPTION]
{self._generate_description(analysis).replace('🔔', '[SUBSCRIBE]')}

#content #monetization #{analysis.content_type.value}
"""
        # Write with UTF-8 encoding
        output_file.write_text(script, encoding='utf-8')
        return str(output_file)
    
    @retry_on_failure()
    @timed_operation()
    def _transform_to_article(self, text: str, analysis: ContentAnalysis) -> str:
        """Transform content into a structured article with SEO optimization"""
        output_file = self.config.output_dir / f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Use text-based emojis instead of Unicode emojis for better compatibility
        content = f"""# {self._generate_title(analysis, use_emoji=False)}

*Generated {datetime.now().strftime('%Y-%m-%d')} | {analysis.word_count} words*

## Introduction
{self._generate_intro(analysis).replace('🔥', '[HOT] ').replace('⚠️', '[WARNING] ')}

## Main Content
{self._structure_content(text, analysis)}

## Conclusion
{self._generate_conclusion(analysis)}

### Key Takeaways
{self._generate_key_points(text)}

*Tags: {', '.join(self._generate_tags(analysis))}*
"""
        # Apply SEO optimization
        content = self._optimize_for_seo(content, analysis)
        
        # Write with UTF-8 encoding
        output_file.write_text(content, encoding='utf-8')
        return str(output_file)
    
    def _transform_to_newsletter(self, text: str, analysis: ContentAnalysis) -> str:
        """Transform content into a newsletter format"""
        output_file = self.config.output_dir / f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Use text-based emojis for better compatibility
        content = f"""# [NEWSLETTER] {self._generate_title(analysis, for_email=True, use_emoji=False)}

{self._generate_intro(analysis).replace('🔥', '[HOT] ').replace('⚠️', '[WARNING] ')}

---

{self._structure_content(text, analysis, for_email=True)}

---

[TIP] **Pro Tip:** {self._generate_pro_tip(analysis)}

[CHART] **Monetization Potential:** {analysis.monetization_potential}/100

[LINK] **Recommended Platforms:** {', '.join(analysis.recommended_platforms[:3])}

[DATE] *Sent on {datetime.now().strftime('%B %d, %Y')}*
"""
        # Write with UTF-8 encoding
        output_file.write_text(content, encoding='utf-8')
        return str(output_file)
    
    def _transform_for_social(self, text: str, analysis: ContentAnalysis) -> str:
        """Create social media posts from content"""
        output_file = self.config.output_dir / f"social_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Truncate and format for social media
        main_text = ' '.join(text.split()[:200]) + ('...' if len(text.split()) > 200 else '')
        
        # Use text-based emojis for better compatibility
        content = f"""[STAR] {self._generate_title(analysis, for_social=True, use_emoji=False)}

{main_text}

[IDEA] {self._generate_engagement_prompt(analysis)}

[LINK] Read more: [LINK]
[CHART] Monetization Potential: {analysis.monetization_potential}/100

{' '.join('#' + tag for tag in self._generate_tags(analysis))}
"""
        # Write with UTF-8 encoding
        output_file.write_text(content, encoding='utf-8')
        return str(output_file)
    
    def _transform_business_initiative(self, text: str, analysis: ContentAnalysis) -> Dict[str, Any]:
        """
        Process business initiative planning workflow.
        
        Args:
            text: The business initiative description or requirements
            analysis: Content analysis results
            
        Returns:
            Dict containing the workflow results
        """
        if not self.business_initiative_workflow:
            raise RuntimeError("Business Initiative Workflow is not initialized")
        
        self.logger.info("Starting Business Initiative Workflow")
        
        try:
            # Run the workflow asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the workflow with the provided text
            result = loop.run_until_complete(
                self.business_initiative_workflow.run_workflow(text)
            )
            
            # Format the result for the pipeline
            return {
                "success": result.success,
                "output": result.output,
                "steps": [
                    {
                        "agent": step["agent"],
                        "role": step["role"],
                        "success": step["success"],
                        "timestamp": step["timestamp"]
                    }
                    for step in result.steps
                ],
                "workflow_id": result.output.get("workflow_id", ""),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Business Initiative Workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": f"biz_init_error_{int(time.time())}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _generate_title(self, analysis: ContentAnalysis, for_email: bool = False, for_social: bool = False, use_emoji: bool = True) -> str:
        """Generate a compelling title based on content analysis"""
        templates = {
            ContentType.TUTORIAL: [
                "How to {} Like a Pro",
                "The Complete Guide to {}",
                "{}: A Step-by-Step Tutorial"
            ],
            ContentType.REVIEW: [
                "{} Review: Honest Thoughts After Testing",
                "Is {} Worth It? My Honest Review",
                "{}: The Good, The Bad, and The Ugly"
            ],
            ContentType.ANALYSIS: [
                "{}: A Data-Driven Analysis",
                "The Truth About {} (Backed by Data)",
                "{}: Trends, Insights, and Predictions"
            ],
            ContentType.LIST: [
                "Top 10 {} You Need to Know",
                "{}: The Ultimate List",
                "The Best {} for Every Need"
            ],
            ContentType.STORY: [
                "My Experience with {}: What I Learned",
                "{}: A Personal Journey",
                "The Truth About {} (From Someone Who's Been There)"
            ],
            ContentType.BUSINESS_INITIATIVE: [
                "Business Initiative: {}",
                "New Project: {}",
                "{}: A Strategic Plan"
            ]
        }
        
        # Get appropriate template
        template = templates.get(analysis.content_type, ["{}"])[0]
        
        # Extract key topic (simplified - in reality, you'd use NLP)
        topic = "This Topic"  # Placeholder - extract from text
        
        title = template.format(topic)
        
        # Add modifiers based on sentiment
        if use_emoji:
            if analysis.sentiment == "positive":
                title = f"🔥 {title}"
            elif analysis.sentiment == "negative":
                title = f"⚠️ {title}"
        else:
            if analysis.sentiment == "positive":
                title = f"[HOT] {title}"
            elif analysis.sentiment == "negative":
                title = f"[WARNING] {title}"
        
        # Add platform-specific formatting
        if for_email:
            title = f"📧 {title}"
        elif for_social:
            title = title.upper() if len(title) < 50 else title
        
        return title
    
    def _generate_intro(self, analysis: ContentAnalysis) -> str:
        """Generate an engaging introduction"""
        intros = {
            ContentType.TUTORIAL: "In this comprehensive guide, I'll walk you through everything you need to know about {}. Whether you're a beginner or an experienced user, you'll find valuable insights and practical tips.",
            ContentType.REVIEW: "After extensive testing and analysis, I'm ready to share my honest thoughts about {}. In this review, I'll cover the pros, cons, and whether it's worth your time and money.",
            ContentType.ANALYSIS: "In this data-driven analysis, we'll take a deep dive into {}. I've crunched the numbers and analyzed the trends to bring you actionable insights and predictions.",
            ContentType.LIST: "Looking for the best {}? You're in the right place. After thorough research and testing, I've compiled this ultimate list of top picks for every need and budget.",
            ContentType.STORY: "Let me take you on a journey through my experience with {}. Along the way, I'll share the lessons I've learned and the insights I've gained.",
            ContentType.BUSINESS_INITIATIVE: "This business initiative aims to {} by leveraging {} and {}."
        }
        
        return intros.get(analysis.content_type, "In this article, we'll explore {} in detail.").format("this topic")
    
    def _generate_conclusion(self, analysis: ContentAnalysis) -> str:
        """Generate a compelling conclusion"""
        conclusions = {
            ContentType.TUTORIAL: "You now have all the tools and knowledge you need to succeed with {}. Remember, practice makes perfect, so don't be afraid to experiment and make it your own.",
            ContentType.REVIEW: "After careful consideration, I can confidently say that {} is {}. While it's not perfect, it offers great value for the right audience.",
            ContentType.ANALYSIS: "The data clearly shows that {} is {}. By keeping these insights in mind, you'll be well-positioned to make informed decisions moving forward.",
            ContentType.LIST: "There you have it - the ultimate list of {}. Whether you're a beginner or an expert, there's something here for everyone. Which one will you try first?",
            ContentType.STORY: "Looking back on my journey with {}, I'm reminded that {}. I hope my experience has provided you with valuable insights and inspiration for your own path.",
            ContentType.BUSINESS_INITIATIVE: "By following this strategic plan, we can achieve our goals and drive business success."
        }
        
        return conclusions.get(analysis.content_type, "In conclusion, {} offers {}. I hope you found this analysis helpful and informative.").format("this topic", "great potential" if analysis.monetization_potential > 70 else "some interesting possibilities")
    
    def _structure_content(self, text: str, analysis: ContentAnalysis, for_email: bool = False) -> str:
        """Structure the main content based on content type"""
        if analysis.content_type == ContentType.LIST:
            return self._format_as_list(text, for_email)
        elif analysis.content_type == ContentType.TUTORIAL:
            return self._format_as_steps(text)
        return text  # Default: return as-is
    
    def _format_as_list(self, text: str, for_email: bool = False) -> str:
        """Format content as a numbered or bulleted list"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        formatted = []
        
        for i, line in enumerate(lines, 1):
            if for_email:
                formatted.append(f"👉 **{i}. {line}**")
            else:
                formatted.append(f"{i}. {line}")
            
            if for_email and i % 3 == 0 and i < len(lines):
                formatted.append("")  # Add space for better email readability
        
        return '\n'.join(formatted)
    
    def _format_as_steps(self, text: str) -> str:
        """Format content as step-by-step instructions"""
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        steps = []
        
        for i, sentence in enumerate(sentences, 1):
            steps.append(f"### Step {i}: {sentence.capitalize()}")
            steps.append("")  # Empty line for readability
        
        return '\n'.join(steps)
    
    def _generate_key_points(self, text: str) -> str:
        """Extract or generate key points from the content"""
        # In a real implementation, you'd use NLP to extract key points
        # For now, we'll just return a placeholder
        return """- Key point 1
- Key point 2
- Key point 3"""
    
    def _generate_tags(self, analysis: ContentAnalysis) -> List[str]:
        """Generate relevant tags based on content analysis"""
        tags = [analysis.content_type.value]
        
        # Add semantic field tags
        for field, score in analysis.semantic_fields.items():
            if score > 0.2:  # Only include significant fields
                tags.append(field)
        
        # Add sentiment tag
        tags.append(analysis.sentiment)
        
        # Add competition level
        tags.append(f"competition_{analysis.competition_level}")
        
        return list(set(tags))  # Remove duplicates
    
    def _generate_pro_tip(self, analysis: ContentAnalysis) -> str:
        """Generate a relevant pro tip based on content type"""
        tips = {
            ContentType.TUTORIAL: "Break down complex tasks into smaller, manageable steps for better learning retention.",
            ContentType.REVIEW: "Always test products in real-world conditions for the most accurate review.",
            ContentType.ANALYSIS: "Look for patterns and trends rather than focusing on individual data points.",
            ContentType.LIST: "Update your lists regularly to keep them relevant and accurate.",
            ContentType.STORY: "Personal anecdotes make your content more relatable and engaging.",
            ContentType.BUSINESS_INITIATIVE: "Clearly define project goals and objectives to ensure everyone is on the same page."
        }
        return tips.get(analysis.content_type, "Quality content always provides value to your audience.")
    
    def _generate_engagement_prompt(self, analysis: ContentAnalysis) -> str:
        """Generate a call-to-action or question to encourage engagement"""
        prompts = {
            ContentType.TUTORIAL: "What was your biggest takeaway from this tutorial?",
            ContentType.LIST: "Which item on this list was most surprising to you?",
            ContentType.REVIEW: "Do you agree with this review? Share your thoughts!",
            ContentType.ANALYSIS: "What's your perspective on this analysis?",
            ContentType.STORY: "How did this story resonate with you?",
            ContentType.BUSINESS_INITIATIVE: "What do you think is the most important aspect of this initiative?"
        }
        return prompts.get(analysis.content_type, "What are your thoughts on this?")
        
    def _generate_description(self, analysis: ContentAnalysis) -> str:
        """Generate a YouTube video description based on content analysis"""
        # Create description with proper encoding
        description = f"""In this video, we explore {analysis.content_type.value} content with a focus on {', '.join(analysis.semantic_fields.keys())}.

"""
        
        # Add relevant hashtags
        tags = self._generate_tags(analysis)[:10]  # Use first 10 tags
        description += "\n".join(f"#{tag.replace(' ', '')}" for tag in tags)
        
        # Add call to action with emoji that works across platforms
        description += "\n\n[Subscribe] Subscribe for more content like this!"
        
        return description
        
    def _calculate_seo_score(self, text: str, title: str) -> Dict[str, Any]:
        """Calculate basic SEO score for content"""
        if not self.config.enable_seo_optimization:
            return {'score': 100, 'recommendations': []}
        
        score = 100
        recommendations = []
        
        # Check title length (optimal: 30-60 characters)
        title_length = len(title)
        if title_length < 30:
            score -= 10
            recommendations.append("Title too short - aim for 30-60 characters")
        elif title_length > 60:
            score -= 5
            recommendations.append("Title too long - consider shortening for better display")
        
        # Check content length
        word_count = len(text.split())
        if word_count < self.config.min_content_length:
            score -= 15
            recommendations.append(f"Content too short ({word_count} words) - aim for at least {self.config.min_content_length} words")
        
        # Check for keyword density (basic check)
        keywords = ['how', 'what', 'why', 'when', 'where', 'tutorial', 'guide', 'learn']
        keyword_density = sum(1 for word in text.lower().split() if any(kw in word for kw in keywords)) / max(word_count, 1) * 100
        if keyword_density > 5:
            score -= 5
            recommendations.append("High keyword density - consider more natural language")
        
        # Check for headings
        heading_count = len(re.findall(r'^#+\s', text, re.MULTILINE))
        if heading_count < 2:
            score -= 10
            recommendations.append("Add more headings (H1, H2, H3) to improve structure")
        
        return {
            'score': max(0, score),
            'recommendations': recommendations,
            'metrics': {
                'title_length': title_length,
                'word_count': word_count,
                'keyword_density': keyword_density,
                'heading_count': heading_count
            }
        }
    
    def _optimize_for_seo(self, content: str, analysis: ContentAnalysis) -> str:
        """Apply basic SEO optimizations to content"""
        if not self.config.enable_seo_optimization:
            return content
        
        # Add meta description suggestion
        meta_desc = f"<!-- SEO Meta Description: {self._generate_title(analysis, use_emoji=False)[:155]}... -->"
        
        # Add alt text suggestions for images (placeholder)
        content = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)', r'![SEO: Add descriptive alt text for "\1"](\2)', content)
        
        return meta_desc + "\n\n" + content

async def run_business_initiative_example():
    """Example usage of the Business Initiative Workflow"""
    from app.agents import BusinessInitiativeWorkflow
    
    # In a real application, you would use the pipeline like this:
    # pipeline = MonetizationPipeline()
    # result = pipeline.process("Launch a new AI-powered customer support tool")
    
    # For demonstration, we'll use the workflow directly
    print("🚀 Starting Business Initiative Workflow Example")
    
    # Initialize the workflow (in a real app, this would be done by the pipeline)
    workflow = BusinessInitiativeWorkflow(assistant=None)  # Pass actual assistant instance
    
    # Example 1: Complete business initiative request
    print("\n📋 Example 1: Complete Business Initiative")
    complete_request = """
    We need to launch a new AI-powered customer support tool by Q3 2024.
    We have a team of 5 developers and a budget of $150,000.
    The goal is to reduce customer support response time by 50% and increase
    customer satisfaction scores by 30% within 6 months of launch.
    """
    
    print("\n📝 Processing complete business initiative...")
    result = await workflow.run_workflow(complete_request)
    
    if result.success:
        print("✅ Success! Launch plan generated:")
        print(result.output.get("launch_plan", "No launch plan generated"))
    else:
        print("❌ Failed to generate launch plan:")
        print(result.output.get("error", "Unknown error"))
    
    # Example 2: Incomplete request (missing details)
    print("\n📋 Example 2: Incomplete Business Initiative")
    incomplete_request = "I want to start a new project next year."
    
    print("\n📝 Processing incomplete business initiative...")
    result = await workflow.run_workflow(incomplete_request)
    
    if not result.success and "missing_info_request" in result.output:
        print("ℹ️ Additional information needed:")
        print(result.output["missing_info_request"])
    
    print("\n🎉 Business Initiative Workflow example completed!")

def main():
    """Example usage of the enhanced MonetizationPipeline"""
    # Run the business initiative example
    print("Starting Business Initiative Workflow Example...")
    asyncio.run(run_business_initiative_example())
    
    # Rest of the original main function...
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Progress callback function
    def progress_callback(message: str, progress: float):
        print(f"📊 Progress: {message} ({progress:.1%})")
    # Example content
    sample_content = """
    In this tutorial, I'll show you how to build a simple web scraper using Python. 
    Web scraping is a valuable skill that can save you hours of manual work. 
    We'll use the requests and BeautifulSoup libraries to extract data from websites.
    
    First, let's install the required packages:
    1. Open your terminal and run: pip install requests beautifulsoup4
    2. Create a new Python file and import the necessary modules
    3. Write code to fetch and parse a webpage
    4. Extract the data you need using CSS selectors
    5. Save the results to a CSV file
    
    With these skills, you can scrape product prices, news articles, and more!
    """
    
    print("🚀 Enhanced MonetizationPipeline Demo")
    print("=" * 50)
    
    # Test 1: Performance monitoring
    print("\n📋 Test 1: Performance Monitoring & Progress Reporting")
    config = PipelineConfig(
        debug=True,
        enable_performance_monitoring=True,
        enable_benchmarking=True,
        progress_callback=progress_callback,
        enable_seo_optimization=True
    )
    pipeline = MonetizationPipeline(config)
    
    start_time = time.time()
    result = pipeline.process(sample_content, output_formats=['article'])
    total_time = time.time() - start_time
    
    print(f"✅ Successes: {len(result.successes)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Warnings: {len(result.warnings)}")
    print(f"⏱️ Total time: {total_time:.3f}s")
    print(f"⏱️ Pipeline time: {result.total_time:.3f}s")
    
    if result.operation_times:
        print("Operation timings:")
        for op, duration in result.operation_times.items():
            print(f"  - {op}: {duration:.3f}s")
    
    # Test 2: SEO Analysis
    print("\n📋 Test 2: SEO Analysis")
    if result.successes:
        article_path = result.successes['article']
        with open(article_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        
        title = pipeline._generate_title(pipeline.microscope.analyze(sample_content), use_emoji=False)
        seo_score = pipeline._calculate_seo_score(article_content, title)
        
        print(f"📈 SEO Score: {seo_score['score']}/100")
        print("SEO Metrics:")
        for metric, value in seo_score['metrics'].items():
            print(f"  - {metric}: {value}")
        
        if seo_score['recommendations']:
            print("SEO Recommendations:")
            for rec in seo_score['recommendations']:
                print(f"  - {rec}")
    
    # Test 3: Retry Logic (simulate failure)
    print("\n📋 Test 3: Retry Logic Demonstration")
    # This would normally demonstrate retry behavior with actual failures
    
    # Test 4: Configuration from environment
    print("\n📋 Test 4: Environment Configuration")
    env_config = PipelineConfig.from_env()
    env_pipeline = MonetizationPipeline(env_config)
    print(f"📋 Config loaded - Debug: {env_config.debug}, SEO: {env_config.enable_seo_optimization}")
    
    print("\n🎉 Enhanced demo completed!")

if __name__ == "__main__":
    main()