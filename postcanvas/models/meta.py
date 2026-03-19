from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MetaConfig(BaseModel):
    """Non-rendered metadata – useful for tracking, CMS integration, etc."""
    title:       Optional[str]       = None
    description: Optional[str]       = None
    tags:        List[str]           = Field(default_factory=list)
    author:      Optional[str]       = None
    created_at:  Optional[str]       = None
    custom:      Dict[str, Any]      = Field(default_factory=dict)
