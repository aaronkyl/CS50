import nltk

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        # code idea from https://stackoverflow.com/questions/6763414/what-is-the-easiest-way-to-get-all-strings-that-do-not-start-with-a-character
        self.positives = set(line.strip() for line in open(positives) if not line.startswith(";"))
        self.negatives = set(line.strip() for line in open(negatives) if not line.startswith(";"))
        self.tokenizer = nltk.tokenize.TweetTokenizer()

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        score = 0
        tokens = self.tokenizer.tokenize(text)
        for word in tokens:
            if word.lower() in self.positives:
                score += 1
            elif word.lower() in self.negatives:
                score -= 1
        return score
