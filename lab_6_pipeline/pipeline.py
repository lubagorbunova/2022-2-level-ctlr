"""
Pipeline for CONLL-U formatting
"""
import re
from pathlib import Path
from typing import List
from difflib import SequenceMatcher

from core_utils.article.article import Article, split_by_sentence
from core_utils.article.article import SentenceProtocol
from core_utils.article.ud import OpencorporaTagProtocol, TagConverter
from core_utils.constants import ASSETS_PATH
from core_utils.article.io import to_cleaned, from_raw


class EmptyDirectoryError(Exception):
    """
    a directory is empty
    """


class InconsistentDatasetError(Exception):
    """
     IDs contain slips, number of meta and raw files is not equal, files are empty
    """

# pylint: disable=too-few-public-methods
class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: Path):
        """
        Initializes CorpusManager
        """
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._validate_dataset()
        self._scan_dataset()

    def _validate_dataset(self) -> None:
        """
        Validates folder with assets
        """
        meta_files = list(self.path_to_raw_txt_data.glob('*_meta.json'))
        raw_files = list(self.path_to_raw_txt_data.glob('*_raw.txt'))
        meta_files_list = [str(x) for x in meta_files]
        meta_files_list.sort()
        raw_files_list = [str(x) for x in raw_files]
        raw_files_list.sort()
        max_number = len(meta_files_list)
        path = str(self.path_to_raw_txt_data)

        if not self.path_to_raw_txt_data.exists():
            raise FileNotFoundError

        if not self.path_to_raw_txt_data.is_dir():
            raise NotADirectoryError

        if max_number == 0:
            raise EmptyDirectoryError

        if len(meta_files_list) != len(raw_files_list):
            raise InconsistentDatasetError
        for file in meta_files:
            if file.stat().st_size == 0:
                raise InconsistentDatasetError
        for file in raw_files:
            if file.stat().st_size == 0:
                raise InconsistentDatasetError
        for i in range(max_number):
            filename = f'{path}\{str(i+1)}_raw.txt'
            print(filename)
            if filename not in raw_files_list:
                raise InconsistentDatasetError

    def _scan_dataset(self) -> None:
        """
        Register each dataset entry
        """
        files_list = list(self.path_to_raw_txt_data.glob('*.*'))
        max_number = int(len(files_list) / 2)
        for i in range(max_number):
            article = Article(url=None, article_id=i)
            self._storage[i + 1] = article

    def get_articles(self) -> dict:
        """
        Returns storage params
        """
        return self._storage

class MorphologicalTokenDTO:
    """
    Stores morphological parameters for each token
    """

    def __init__(self, lemma: str = "", pos: str = "", tags: str = ""):
        """
        Initializes MorphologicalTokenDTO
        """
        self.lemma = ''
        self.pos = ''
        self.tags = ''


class ConlluToken:
    """
    Representation of the CONLL-U Token
    """

    def __init__(self, text: str):
        """
        Initializes ConlluToken
        """
        self._text = text

    def set_morphological_parameters(self, parameters: MorphologicalTokenDTO) -> None:
        """
        Stores the morphological parameters
        """

    def get_morphological_parameters(self) -> MorphologicalTokenDTO:
        """
        Returns morphological parameters from ConlluToken
        """

    def get_conllu_text(self, include_morphological_tags: bool) -> str:
        """
        String representation of the token for conllu files
        """

    def get_cleaned(self) -> str:
        """
        Returns lowercase original form of a token
        """
        return self._text.lower()

class ConlluSentence(SentenceProtocol):
    """
    Representation of a sentence in the CONLL-U format
    """

    def __init__(self, position: int, text: str, tokens: list[ConlluToken]):
        """
        Initializes ConlluSentence
        """
        self._position = position
        self._tokens = tokens
        self._text = text

    def get_conllu_text(self, include_morphological_tags: bool) -> str:
        """
        Creates string representation of the sentence
        """

    def get_cleaned_sentence(self) -> str:
        """
        Returns the lowercase representation of the sentence
        """
        sentence = ''
        for word in self._tokens:
            sentence += word.get_cleaned()
        return sentence

    def get_tokens(self) -> list[ConlluToken]:
        """
        Returns sentences from ConlluSentence
        """
        return self._tokens


class MystemTagConverter(TagConverter):
    """
    Mystem Tag Converter
    """

    def convert_morphological_tags(self, tags: str) -> str:  # type: ignore
        """
        Converts the Mystem tags into the UD format
        """

    def convert_pos(self, tags: str) -> str:  # type: ignore
        """
        Extracts and converts the POS from the Mystem tags into the UD format
        """


class OpenCorporaTagConverter(TagConverter):
    """
    OpenCorpora Tag Converter
    """

    def convert_pos(self, tags: OpencorporaTagProtocol) -> str:  # type: ignore
        """
        Extracts and converts POS from the OpenCorpora tags into the UD format
        """

    def convert_morphological_tags(self, tags: OpencorporaTagProtocol) -> str:  # type: ignore
        """
        Converts the OpenCorpora tags into the UD format
        """


class MorphologicalAnalysisPipeline:
    """
    Preprocesses and morphologically annotates sentences into the CONLL-U format
    """

    def __init__(self, corpus_manager: CorpusManager):
        """
        Initializes MorphologicalAnalysisPipeline
        """
        self._corpus = corpus_manager

    def _process(self, text: str) -> List[ConlluSentence]:
        """
        Returns the text representation as the list of ConlluSentence
        """
        conllu_sentences = []
        sentences = split_by_sentence(text)
        for position, sentence in enumerate(sentences):
            conllu_list = []
            for text in sentence.split():
                conllu_list.append(ConlluToken(text))
            conllu_sentences.append(ConlluSentence(position, sentence, conllu_list))
        return conllu_sentences

    def run(self) -> None:
        """
        Performs basic preprocessing and writes processed text to files
        """
        for article in self._corpus.get_articles().values():
            #from_raw(article.url, article)
            sentences = self._process(article.text)
            article.set_conllu_sentences(sentences)
            to_cleaned(article)


class AdvancedMorphologicalAnalysisPipeline(MorphologicalAnalysisPipeline):
    """
    Preprocesses and morphologically annotates sentences into the CONLL-U format
    """

    def __init__(self, corpus_manager: CorpusManager):
        """
        Initializes MorphologicalAnalysisPipeline
        """

    def _process(self, text: str) -> List[ConlluSentence]:
        """
        Returns the text representation as the list of ConlluSentence
        """

    def run(self) -> None:
        """
        Performs basic preprocessing and writes processed text to files
        """


def main() -> None:
    """
    Entrypoint for pipeline module
    """
    path = Path(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=path)
    pipeline = MorphologicalAnalysisPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
