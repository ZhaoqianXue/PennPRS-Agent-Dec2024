
import pytest
import os
from unittest.mock import patch
from src.core.llm_config import get_llm, get_config, LLMConfig, ModelConfig, list_configs
from langchain_openai import ChatOpenAI

@pytest.fixture(autouse=True)
def mock_openai_key():
    """Mock OpenAI API key for all tests to avoid initialization errors."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-dummy-key-for-testing"}):
        yield

class TestLLMConfig:
    """Tests for the centralized LLM configuration module."""

    def test_default_config(self):
        """Test retrieving the default configuration."""
        llm = get_llm("default")
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == LLMConfig.DEFAULT.model
        # LangChain may normalize 0.0 to None/default
        if LLMConfig.DEFAULT.temperature == 0.0:
            assert llm.temperature == 0.0 or llm.temperature is None
        else:
            assert llm.temperature == LLMConfig.DEFAULT.temperature

    def test_specific_module_config(self):
        """Test retrieving configuration for a specific module."""
        # Test Literature Classifier config
        llm = get_llm("literature_classifier")
        config = get_config("literature_classifier")
        
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == config.model
        
        if config.temperature == 0.0:
             assert llm.temperature == 0.0 or llm.temperature is None
        elif llm.temperature is not None:
             assert llm.temperature == config.temperature
        
        # Verify JSON mode if applicable
        if config.json_mode:
            assert llm.model_kwargs.get("response_format") == {"type": "json_object"}

    def test_unknown_module_fallback(self):
        """Test that unknown modules fall back to default."""
        llm = get_llm("non_existent_module")
        assert llm.model_name == LLMConfig.DEFAULT.model
        if LLMConfig.DEFAULT.temperature == 0.0:
            assert llm.temperature == 0.0 or llm.temperature is None
        else:
            assert llm.temperature == LLMConfig.DEFAULT.temperature

    def test_openai_model_env_override(self):
        """Test OPENAI_MODEL environment variable override."""
        with patch.dict(os.environ, {"OPENAI_MODEL": "gpt-test-override"}):
            llm = get_llm("default")
            assert llm.model_name == "gpt-test-override"

    def test_model_config_to_dict(self):
        """Test ModelConfig to dict conversion."""
        config = ModelConfig(
            model="gpt-test",
            temperature=0.7,
            max_tokens=100,
            timeout=50,
            json_mode=True
        )
        
        config_dict = config.to_dict()
        assert config_dict["model"] == "gpt-test"
        assert config_dict["temperature"] == 0.7
        assert config_dict["max_tokens"] == 100
        assert config_dict["timeout"] == 50
        assert config_dict["model_kwargs"] == {"response_format": {"type": "json_object"}}

    def test_list_configs(self):
        """Test listing all configurations."""
        configs = list_configs()
        assert isinstance(configs, dict)
        assert "default" in configs
        assert "literature_classifier" in configs
        assert "literature_extractor" in configs

    def test_config_consistency(self):
        """Ensure all defined configs in LLMConfig are accessible via get_llm."""
        # Check a sample of critical configs
        critical_configs = [
            "literature_classifier", 
            "paper_classifier", 
            "literature_extractor", 
            "prs_extractor"
        ]
        
        for module_name in critical_configs:
            llm = get_llm(module_name)
            assert isinstance(llm, ChatOpenAI)
            
