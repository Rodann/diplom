import pke
import spacy
from aiochan import Chan
from config import keywords_count


async def get_keywords(channel: Chan, text):
    nlp = spacy.load('ru_core_news_sm')
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(
        input=text,
        language='ru'
    )
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=keywords_count)
    output = []
    for i in keyphrases:
        phrase = nlp(i[0])
        keyphrase = ''
        for token in phrase:
            if len(keyphrase) > 0:
                keyphrase += f' {token.lemma_}'
            else:
                keyphrase += token.lemma_
        output.append((keyphrase, i[1]))
    channel.put(output)


async def get_similar(channel: Chan, word1, word2):
    # ставлю порог сходства 0.4 если сходство больше то попадает в категорию
    nlp = spacy.load('ru_core_news_sm')
    words = f"{word1} {word2}"
    tokens = nlp(words)
    token1, token2 = tokens[0], tokens[1]
    channel.put(token1.similarity(token2))
