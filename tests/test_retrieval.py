from polaris_core.models import Document
from polaris_core.retrieval import LocalRetriever, chunk_text, tokenize


def test_tokenize_handles_accents():
    assert tokenize("Sísmica e inversão!") == ["sísmica", "e", "inversão"]


def test_chunk_text_uses_overlap():
    chunks = chunk_text("one two three four five", max_words=3, overlap=1)
    assert chunks == ["one two three", "three four five"]


def test_local_retriever_finds_relevant_chunk():
    retriever = LocalRetriever(
        documents=[
            Document(id="1", name="wells.md", text="Alpha well has gamma ray and density logs."),
            Document(id="2", name="seismic.md", text="Seismic inversion estimates impedance volumes."),
        ]
    )

    results = retriever.search("impedance inversion")

    assert results
    assert results[0].document_name == "seismic.md"
    assert "impedance" in results[0].chunk


def test_local_retriever_loads_single_file_path(tmp_path):
    path = tmp_path / "andromeda.txt"
    path.write_text("Andromeda software supports geophysical workflows.", encoding="utf-8")

    retriever = LocalRetriever.from_path(path)
    results = retriever.search("What is Andromeda software?")

    assert len(retriever.documents) == 1
    assert retriever.documents[0].name == "andromeda.txt"
    assert results
    assert "Andromeda software" in results[0].chunk


def test_local_retriever_loads_pdf_text(tmp_path):
    import fitz

    path = tmp_path / "rock_physics.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Rock physics links impedance to porosity.")
    document.save(str(path))
    document.close()

    retriever = LocalRetriever.from_path(path)
    results = retriever.search("impedance porosity")

    assert len(retriever.documents) == 1
    assert retriever.documents[0].name == "rock_physics.pdf"
    assert retriever.documents[0].metadata["source_type"] == "pdf"
    assert results
    assert "impedance" in results[0].chunk


def test_local_retriever_loads_supported_files_recursively(tmp_path):
    nested = tmp_path / "books" / "geophysics"
    nested.mkdir(parents=True)
    path = nested / "seismic.md"
    path.write_text("Seismic attributes can support stratigraphic interpretation.", encoding="utf-8")

    retriever = LocalRetriever.from_path(tmp_path)

    assert len(retriever.documents) == 1
    assert retriever.documents[0].name == "seismic.md"
