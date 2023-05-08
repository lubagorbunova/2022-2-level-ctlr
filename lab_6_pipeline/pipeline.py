"""
Pipeline for CONLL-U formatting
"""
from pathlib import Path
from typing import List
import string
import re

from core_utils.article.article import split_by_sentence
from core_utils.article.article import SentenceProtocol
from core_utils.article.ud import OpencorporaTagProtocol, TagConverter
from core_utils.constants import ASSETS_PATH
from core_utils.article.io import to_cleaned, from_raw, to_conllu


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
        #meta_files = list(self.path_to_raw_txt_data.glob('*_meta.json'))
        raw_files = list(self.path_to_raw_txt_data.glob('*_raw.txt'))
        #meta_files_list = [str(x) for x in meta_files]
        raw_files_list = [str(x) for x in raw_files]
        max_number = len(raw_files_list)
        path = str(self.path_to_raw_txt_data)

        if not self.path_to_raw_txt_data.exists():
            raise FileNotFoundError

        if not self.path_to_raw_txt_data.is_dir():
            raise NotADirectoryError

        if max_number == 0:
            raise EmptyDirectoryError

        #if len(meta_files_list) != len(raw_files_list):
        #    raise InconsistentDatasetError
        #for file in meta_files:
        #    if not file.stat().st_size:
        #        raise InconsistentDatasetError
        for file in raw_files:
            if not file.stat().st_size:
                raise InconsistentDatasetError
        for i in range(max_number):
            filename_raw = path + '\\' + str(i+1) + '_raw.txt'
        #    filename_meta = path + '\\' + str(i + 1) + '_meta.json'
            if filename_raw not in raw_files_list: #or filename_meta not in meta_files_list:
                raise InconsistentDatasetError
            #test data in github?

    def _scan_dataset(self) -> None:
        """
        Register each dataset entry
        """
        files_list = self.path_to_raw_txt_data.glob('*_raw.txt')
        for file in files_list:
            article = from_raw(file)
            self._storage.update({article.article_id: article})

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
        self.lemma = ""
        self.pos = ""
        self.tags = ""


class ConlluToken:
    """
    Representation of the CONLL-U Token
    """

    def __init__(self, text: str):
        """
        Initializes ConlluToken
        """
        self._text = text
        parameters = MorphologicalTokenDTO()
        self._morphological_parameters = parameters
        self.position = 0

    def set_morphological_parameters(self, parameters: MorphologicalTokenDTO) -> None:
        """
        Stores the morphological parameters
        """
        self._morphological_parameters.tags = parameters.tags
        self._morphological_parameters.pos = parameters.pos
        self._morphological_parameters.lemma = parameters.lemma

    def get_morphological_parameters(self) -> MorphologicalTokenDTO:
        """
        Returns morphological parameters from ConlluToken
        """
        return self._morphological_parameters

    def get_conllu_text(self, include_morphological_tags: bool) -> str:
        """
        String representation of the token for conllu files
        """
        res = str(self.position) + '\t' + self._text + '\t' + self._morphological_parameters.lemma + '\t' \
                 + self._morphological_parameters.pos + '\t' + '_' + '\t' + '_'+ '\t' + '0' + '\t' \
                 + 'root' + '\t' + '_' + '\t' + '_'
        return res

    def get_cleaned(self) -> str:
        """
        Returns lowercase original form of a token
        """
        text = self._text
        res = re.sub(r'[^\w\s]', '', text)
        return res.lower()


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
        return f'# sent_id = {self._position}\n' + \
               f'# text = {self._text}\n' + self._format_tokens(include_morphological_tags)

    def get_cleaned_sentence(self) -> str:
        """
        Returns the lowercase representation of the sentence
        """
        sentence = ''
        for word in self._tokens:
            sentence += ' '+word.get_cleaned()
        return ' '.join(sentence.split()).lower()

    def get_tokens(self) -> list[ConlluToken]:
        """
        Returns sentences from ConlluSentence
        """
        return self._tokens

    def _format_tokens(self, include_morphological_tags: bool) -> str:
        """
        formats tokens per newline
        """
        res = ''
        for token in self._tokens:
            text = token.get_conllu_text(include_morphological_tags)
            res += text + '\n'
        return res


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
            sentences = self._process(article.text)
            article.set_conllu_sentences(sentences)
            to_cleaned(article)
            #to_conllu(article)

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
