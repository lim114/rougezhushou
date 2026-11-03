def font_setup_source_fragment(os, Path, QFontDatabase):
    font_file=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/msyh.ttc'
    font_id=QFontDatabase.addApplicationFont(str(font_file));families=QFontDatabase.applicationFontFamilies(font_id)
    if families:
        font_family=families[0]
    else:
        # This synthetic OCR fixture needs a real CJK font. Keep the native
        # font first; an explicit portable font never impersonates msyh.
        configured_font=os.environ.get('ROUGE_TEST_CJK_FONT')
        if not configured_font:
            raise RuntimeError('CJK font fixture unavailable: '+str(font_file)+
                '; set ROUGE_TEST_CJK_FONT to a real font file containing Noto Sans CJK SC.')
        fallback_file=Path(configured_font)
        if not fallback_file.is_file():
            raise RuntimeError('Configured CJK font fixture file is unavailable: '+str(fallback_file))
        fallback_id=QFontDatabase.addApplicationFont(str(fallback_file))
        fallback_families=QFontDatabase.applicationFontFamilies(fallback_id)
        if 'Noto Sans CJK SC' not in fallback_families:
            raise RuntimeError('Configured CJK font fixture has no usable Noto Sans CJK SC family: '+str(fallback_file))
        font_family='Noto Sans CJK SC'
    return font_family
