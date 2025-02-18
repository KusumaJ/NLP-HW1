import sys
from collections import defaultdict
import math
import random
import os
import os.path
"""
COMS W4705 - Natural Language Processing - Spring 2025 
Programming Homework 1 - Trigram Language Models
Daniel Bauer
"""

def corpus_reader(corpusfile, lexicon=None): 
    with open(corpusfile,'r') as corpus: 
        for line in corpus: 
            if line.strip():
                sequence = line.lower().strip().split()
                if lexicon: 
                    yield [word if word in lexicon else "UNK" for word in sequence]
                else: 
                    yield sequence

def get_lexicon(corpus):
    word_counts = defaultdict(int)
    for sentence in corpus:
        for word in sentence: 
            word_counts[word] += 1
    return set(word for word in word_counts if word_counts[word] > 1)  



def get_ngrams(sequence, n):
    """
    COMPLETE THIS FUNCTION (PART 1)
    Given a sequence, this function should return a list of n-grams, where each n-gram is a Python tuple.
    This should work for arbitrary values of n >= 1 
    """
    sequence = ["START"]*(n-1) + sequence + ["STOP"]
    newseq = []
    for i in range(0,len(sequence)-n+1):
        newseq += [tuple(sequence[i:i+n])]
    return newseq


class TrigramModel(object):
    
    def __init__(self, corpusfile):
    
        # Iterate through the corpus once to build a lexicon 
        generator = corpus_reader(corpusfile)
        self.lexicon = get_lexicon(generator)
        self.lexicon.add("UNK")
        self.lexicon.add("START")
        self.lexicon.add("STOP")
    
        # Now iterate through the corpus again and count ngrams
        generator = corpus_reader(corpusfile, self.lexicon)
        self.count_ngrams(generator)


    def count_ngrams(self, corpus):
        """
        COMPLETE THIS METHOD (PART 2)
        Given a corpus iterator, populate dictionaries of unigram, bigram,
        and trigram counts. 
        """
   
        self.unigramcounts = {} # might want to use defaultdict or Counter instead
        self.bigramcounts = {} 
        self.trigramcounts = {} 
        self.wordcount = 0

        ##Your code here
        
        for c in corpus:
            ngrams = get_ngrams(c,1)
            for g in ngrams: 
                self.unigramcounts[g] = self.unigramcounts.get(g,0)+1
                self.wordcount+=1

            ngrams = get_ngrams(c,2)
            for g in ngrams: self.bigramcounts[g] = self.bigramcounts.get(g,0)+1

            ngrams = get_ngrams(c,3)
            for g in ngrams: self.trigramcounts[g] = self.trigramcounts.get(g,0)+1

        return

    def raw_trigram_probability(self,trigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) trigram probability
        """

        # START START case
        if(trigram[0]=="START" and trigram[1]=="START"): return self.trigramcounts.get(trigram,0)/self.unigramcounts.get(("STOP",))

        # unseen probability
        if self.bigramcounts.get((trigram[0:2]),0)==0:
            return self.raw_unigram_probability((trigram[2],))
            # another way of handling: P(v | u,w) = 1 / |V| 
            # return 1/(len(self.lexicon)) 
        
        return (self.trigramcounts.get(trigram,0)/self.bigramcounts.get((trigram[0:2])))

    def raw_bigram_probability(self, bigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) bigram probability
        """
        if(bigram[0]=="START"): return self.bigramcounts.get(bigram,0)/self.unigramcounts.get(("STOP",))

        if self.unigramcounts.get((bigram[0],),0)==0:
            return self.raw_unigram_probability((bigram[1],))
            # another way of handling P(v | u,w) = 1 / |V| 
            # return 1/(len(self.lexicon)) 

        return self.bigramcounts.get(bigram,0)/self.unigramcounts.get((bigram[0],))
    
    def raw_unigram_probability(self, unigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) unigram probability.
        """

        #hint: recomputing the denominator every time the method is called
        # can be slow! You might want to compute the total number of words once, 
        # store in the TrigramModel instance, and then re-use it.  
        return self.unigramcounts.get(unigram,0)/self.wordcount

    def generate_sentence(self,t=20): 
        """
        COMPLETE THIS METHOD (OPTIONAL)
        Generate a random sentence from the trigram model. t specifies the
        max length, but the sentence may be shorter if STOP is reached.
        """
        return result            

    def smoothed_trigram_probability(self, trigram):
        """
        COMPLETE THIS METHOD (PART 4)
        Returns the smoothed trigram probability (using linear interpolation). 
        """
        lambda1 = 1/3.0
        lambda2 = 1/3.0
        lambda3 = 1/3.0
        return (lambda1*self.raw_trigram_probability(trigram) 
                + lambda2*self.raw_bigram_probability((trigram[1],trigram[2])) 
                + lambda3*self.raw_unigram_probability((trigram[2],)))
        
    def sentence_logprob(self, sentence):
        """
        COMPLETE THIS METHOD (PART 5)
        Returns the log probability of an entire sequence.
        """
        sumprob = 0
        trigrams = get_ngrams(sentence,3)

        for t in trigrams: sumprob += math.log2(self.smoothed_trigram_probability(t))
        
        return sumprob

    def perplexity(self, corpus):
        """
        COMPLETE THIS METHOD (PART 6) 
        Returns the log probability of an entire sequence.
        """
        sumprob = 0
        M = 0
        for c in corpus:
            sumprob += self.sentence_logprob(c)
            M += len(c)+1 # + "STOP" word
        return math.pow(2, -sumprob/M)


def essay_scoring_experiment(training_file1, training_file2, testdir1, testdir2):

        model1 = TrigramModel(training_file1)
        model2 = TrigramModel(training_file2)

        total = 0
        correct = 0       
 
        for f in os.listdir(testdir1):
            pp1 = model1.perplexity(corpus_reader(os.path.join(testdir1, f), model1.lexicon))
            pp2 = model2.perplexity(corpus_reader(os.path.join(testdir1, f), model2.lexicon))
            total+=1
            if(pp1<pp2): correct+=1
    
        for f in os.listdir(testdir2):
            pp1 = model1.perplexity(corpus_reader(os.path.join(testdir2, f), model1.lexicon))
            pp2 = model2.perplexity(corpus_reader(os.path.join(testdir2, f), model2.lexicon))
            total+=1
            if(pp1>pp2): correct+=1
        
        return correct*100/total

if __name__ == "__main__":

    model = TrigramModel(sys.argv[1]) 

    # put test code here...
    # dev_corpus_train = corpus_reader(sys.argv[1], model.lexicon)

    # print("Word Count: ",model.wordcount)
    # print("Training perplexity: ", model.perplexity(dev_corpus_train))

            
    # or run the script from the command line with 
    # $ python -i trigram_model.py [corpus_file]
    # >>> 
    #
    # you can then call methods on the model instance in the interactive 
    # Python prompt. 

    
    # Testing perplexity: 
    # dev_corpus = corpus_reader(sys.argv[2], model.lexicon)
    # pp = model.perplexity(dev_corpus)
    # print("Testing perplexity: ",pp)


    # Essay scoring experiment: 
    # acc = essay_scoring_experiment('train_high.txt', 'train_low.txt", "test_high", "test_low")
    # print(acc)

