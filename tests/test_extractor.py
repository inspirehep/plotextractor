from pathlib import Path

from plotextractor.extractor import extract_captions


def test_get_with_trim(tmpdir):
    latex_filename = str(Path(__file__).parent / "data" / "main_trim.tex")

    partly_extracted_image_data = extract_captions(latex_filename, tmpdir, [])
    assert any(
        "Results_ProtonPion_20240620_NewSyst_CorrectMC/ProtonPion_CF_mT_1.pdf"
        in sublist
        for sublist in partly_extracted_image_data
    )
