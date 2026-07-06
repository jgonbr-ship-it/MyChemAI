# MyChemAI – Implementation TODO

## Document Intelligence subsystem (new)
- [x] Create TODO tracker
- [x] Create packages under `Engine/` (Analysis, NLP, Chemistry, Spectroscopy, Documents/Structure)
- [x] Implement required classes with real logic using existing `document.raw` artifacts
- [x] Provide orchestration facade(s) that processors can call





## Pipeline (next-gen order)
- [ ] Add new processors inheriting `Processor` for: Import, Metadata, Layout, Normalization, Structure, Chemistry, Spectroscopy, Registration
- [ ] Add a `PipelineBuilder` used by `MyChemAI` to compose processors in required order
- [ ] Keep `PipelineManager` unchanged

## PDFReader upgrades
- [ ] Implement `PDFMetadataExtractor` to extract real metadata/fonts/styles and aggregate
- [ ] Implement `PDFImageExtractor` to extract images + positions + captions heuristics
- [ ] Implement `PDFTableExtractor` using available dependencies (real extraction)
- [ ] Ensure backward compatibility for existing `document.raw` fields

## KnowledgeBase upgrades
- [ ] Add relationship graph storage + indexes (in-memory + JSON persistence if storage exists)
- [ ] Keep existing public dicts for backward compatibility
- [ ] Update registration processor to populate relationships

## Search engine
- [ ] Implement `Engine/Search` with indexed search across molecules/reactions/properties/pages/sections
- [ ] Integrate with GUI inspector result model

## GUI non-blocking load
- [ ] Add worker thread for document loading + pipeline execution
- [ ] Update inspector views to show: tree, metadata, sections/tables/figures, entities, spectra, references, stats

## Verification
- [ ] Smoke test: import PDF and ensure no UI freeze
- [ ] Validate metadata/layout/structure extraction output shapes
- [ ] Validate KnowledgeBase relationships and search results

