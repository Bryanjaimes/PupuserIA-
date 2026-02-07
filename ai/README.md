# AI Engine — Gateway El Salvador

This directory contains the four AI systems that power the platform:

## Modules

### 🏠 `valuation/` — Property Valuation Engine
"The Zestimate for El Salvador." Hybrid ML model (XGBoost + Vision Transformer)
trained on scraped listings, cadastral data, and satellite imagery.

### 🤖 `concierge/` — AI Concierge
RAG-powered bilingual chatbot built on Claude API with proprietary ES knowledge base.

### 📝 `content/` — SEO Content Engine
Automated content generation pipeline for blog posts, guides, and property descriptions.

### 🎓 `tutor/` — Edge AI Tutor
Quantized models (ONNX/GGUF) for offline-first education on low-cost devices.
