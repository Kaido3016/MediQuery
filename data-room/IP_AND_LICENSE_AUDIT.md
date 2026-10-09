# MediQuery — IP & Software Licensing Due-Diligence Audit

**Scope:** acquisition-readiness review of the `release/v1.0.0` repository.

**Purpose:** identify ownership, licensing, third-party dependency, model/data, and provenance items a buyer should verify before purchasing MediQuery. This document is a due-diligence inventory, not a legal opinion or representation that all rights have been conclusively established.

## 1. Executive result

**STATUS: CONDITIONAL PASS — LEGAL/IP VERIFICATION REQUIRED BEFORE CLOSING**

The repository is a coherent software asset, but the repository itself does not provide enough evidence to certify clean title to every component. A buyer should require an explicit seller representation of ownership, a third-party dependency/license inventory, and legal review before relying on the asset for a six-figure transaction.

The repository currently has **no `LICENSE` file** visible in the release tree. Therefore the seller should not describe the repository as permissively open-source licensed unless a separate license grant exists outside the repository. The absence of a repository license does not itself prove that the seller lacks ownership; it means the terms of reuse and transfer need to be established contractually.

## 2. Seller-owned asset inventory

The intended transaction asset should be defined in the definitive agreement rather than inferred from filenames. Candidate owned deliverables include:

- MediQuery application source code.
- Backend/API source.
- Streamlit client source.
- Tests and synthetic fixtures authored for the project.
- CI/CD workflow definitions authored for the project.
- Docker and Compose configuration authored for the project.
- Architecture, security, AI-safety, deployment, testing, performance, acquisition, and buyer-due-diligence documentation authored for the project.
- Database models/schema and application configuration authored for the project.
- Project-specific scripts and utilities authored for the project.
- Git history and repository structure, subject to the transfer terms.

The buyer should acquire these explicitly through an IP assignment or asset-purchase agreement rather than relying on transfer of a GitHub repository alone.

## 3. Repository license status

### Finding

No `LICENSE` file was found in the inspected release tree.

### Buyer implication

Before closing, establish:

1. Who owns the copyright in the MediQuery source and documentation.
2. Whether any other person contributed code, documentation, designs, tests, prompts, datasets, or assets.
3. Whether any work was created under employment, school, contractor, volunteer, client, or other assignment terms.
4. Whether any prior agreement restricts transfer or commercialization.
5. What license/ownership terms the buyer will receive under the purchase agreement.

### Recommendation

Do **not** add a permissive open-source license merely to make the repository look more complete unless that is intentionally part of the commercial strategy. For an acquisition, the cleaner approach is normally to document proprietary ownership and transfer terms in the transaction documents, with counsel selecting the appropriate notices and license strategy.

## 4. Contributor and chain-of-title verification

The repository history should be reviewed for authors other than the seller and for commits that may contain third-party contributions.

Seller should provide a signed schedule covering:

- all contributors;
- contribution dates/periods;
- employment/contractor status at the time of contribution;
- written IP assignment or work-for-hire evidence where applicable;
- confirmation that no contributor retained rights that conflict with the sale.

A Git author name alone is not legal proof of copyright ownership.

## 5. Third-party dependency inventory

`requirements.txt` contains a broad set of third-party packages, including FastAPI, Uvicorn, Streamlit, Plotly, Transformers, PyTorch, torchvision, sentence-transformers, FAISS, Pillow, OpenCV, pypdf, NumPy, pandas, scikit-learn, matplotlib, requests/httpx, Pydantic, SQLAlchemy, Redis, PostgreSQL driver, pytest, Black, Flake8, Jupyter/IPython, python-jose, passlib, bcrypt, setuptools and wheel.

The CI dependency set is materially smaller than the full runtime/development requirements. This distinction matters because the buyer should inventory **both** declared dependencies and the dependencies actually imported by production code paths.

The repository's acquisition documentation already identifies third-party dependency/model/data licensing as an outstanding diligence item.

### Buyer verification required

For each dependency used by distributed/runtime code:

- exact version in the acquisition build;
- license identifier and license text;
- direct/transitive status;
- attribution/notice obligations;
- copyleft or source-disclosure implications, if any;
- known commercial-use restrictions;
- security status and end-of-life status;
- whether the dependency is actually necessary.

A Software Bill of Materials (SBOM), preferably generated from the exact release artifact, should be supplied before closing.

## 6. AI/model/data licensing

The repository contains AI/ML-related dependency declarations and retrieval infrastructure, but the acquisition documentation explicitly states that a populated production medical RAG knowledge base and production generative-model integration are not implemented.

Therefore the seller should **not** represent that MediQuery owns:

- a proprietary medical foundation model;
- exclusive medical datasets;
- proprietary medical literature rights;
- exclusive embedding-model rights;
- a licensed production medical knowledge base;
- commercial rights to third-party model weights beyond their actual license terms.

If any local model files, datasets, evaluation corpora, PDFs, or other artifacts exist outside the repository, their provenance and license must be disclosed before inclusion in the transaction.

## 7. Ignored/untracked asset warning

The repository `.gitignore` excludes `models/`, `data/raw/`, `data/processed/`, `results/`, upload directories, local databases, and environment files.

This is normal for secrets and generated/local data, but it creates an acquisition-diligence requirement: **the Git repository is not necessarily the complete universe of files used during development.**

Before closing, the seller should certify whether any excluded local files contain:

- proprietary source code;
- model weights;
- datasets;
- licensed documents;
- evaluation data;
- generated assets required to reproduce a claimed capability;
- third-party material that cannot legally be transferred.

The buyer should receive a clean manifest of all required non-repository artifacts and their legal status.

## 8. Frontend dependency note

`src/frontend/package.json` declares React, React Router, React testing libraries, Axios, react-dropzone, react-hot-toast, lucide-react, Tailwind CSS, PostCSS, and related packages. The buyer should treat these as third-party dependencies and verify their licenses through the exact lockfile/build environment if a frontend package is part of the acquisition deliverables.

The presence of a dependency declaration is not evidence that all associated application source files are present or that a production frontend exists.

## 9. Documentation and branding

Documentation is an asset only to the extent that the seller owns the authored text and has rights to any embedded third-party material. The buyer should verify:

- screenshots and images;
- logos and trademarks;
- copied documentation fragments;
- diagrams generated from third-party templates;
- fonts and UI assets;
- example medical reports or sample data.

No trademark registration or exclusive brand rights should be implied without documentary evidence.

## 10. Medical-content rights

Because MediQuery is healthcare-oriented, a buyer should distinguish software IP from medical-content rights.

The current repository's acquisition documentation does not establish ownership of a proprietary medical corpus, licensed clinical content, or clinical guidelines. Any future use of medical literature, guidelines, reference ranges, or patient-facing educational content must be separately rights-cleared and evaluated for appropriate use.

## 11. Open-source compliance package recommended for closing

Prepare a closing package containing:

- SBOM for the exact release;
- direct dependency list;
- transitive dependency list where practical;
- license identifiers and notices;
- copies/links to applicable license texts;
- attribution file where required;
- list of model/data licenses;
- list of third-party assets;
- list of excluded local/generated artifacts;
- contributor/assignment schedule;
- seller ownership representation;
- known disputes or claims statement.

## 12. Required seller representations

For a six-figure transaction, counsel should consider representations covering at least:

- seller's ownership of the transferred IP;
- authority to sell/assign the IP;
- absence of undisclosed contributors with conflicting rights;
- disclosure of third-party software and applicable licenses;
- disclosure of third-party models/data/assets;
- absence of knowingly infringing material, subject to negotiated scope;
- disclosure of litigation or IP claims, if any;
- disclosure of excluded assets;
- disclosure of open-source obligations;
- accurate identification of what is and is not included in the transaction.

These are transaction/legal matters and should be finalized by qualified counsel.

## 13. Buyer red flags to resolve

| Item | Current repository evidence | Status |
|---|---|---|
| Proprietary source ownership | Project repository exists; legal chain-of-title documents not present | **Needs seller certification/legal evidence** |
| Repository license | No `LICENSE` file found | **Needs explicit transaction terms** |
| Contributors | Git history exists; legal assignments not represented in repo | **Needs verification** |
| Third-party Python packages | Declared in requirements files | **Needs SBOM/license inventory** |
| Node packages | Declared in `package.json` | **Needs exact build/license inventory** |
| Model weights | `models/` excluded by `.gitignore` | **Needs excluded-artifact certification** |
| Datasets/raw data | Raw/processed data excluded | **Needs provenance verification** |
| Medical content rights | No proprietary corpus claimed | **No claim should be made** |
| Trademarks/brand | No exclusive rights evidenced by this audit | **Needs separate verification** |

## 14. Acquisition conclusion

MediQuery can be packaged as a transferable software asset, but **clean IP title is not established merely by having a public GitHub repository**.

For the $100K+ acquisition strategy, the correct message is:

> **The buyer receives the MediQuery software and documentation IP subject to formal chain-of-title, third-party license, and transaction diligence.**

Do not claim:

- "100% proprietary technology" until chain of title is verified;
- "all AI models are owned by MediQuery";
- "exclusive medical dataset";
- "fully licensed medical corpus";
- "patented technology" without patent evidence;
- "compliance certification" based on repository documentation.

## 15. Step-4 acceptance criteria

Step 4 is considered complete from the **repository-preparation** perspective when this audit is included in the Buyer Data Room and the remaining legal actions are explicitly tracked as buyer/seller diligence items.

The following remain external actions before an actual transaction:

- obtain formal legal advice;
- execute/verify contributor IP assignments where applicable;
- generate an SBOM against the final release artifact;
- verify dependency/model/data licenses;
- certify excluded/local artifacts;
- establish definitive IP transfer language;
- determine final proprietary/open-source licensing strategy.

**Final status: READY FOR LEGAL/IP DUE DILIGENCE — NOT A LEGAL CERTIFICATION.**
