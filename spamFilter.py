############################################################
# Imports
############################################################

import os
import email
import math


############################################################
# Section 1: Spam Filter
############################################################


def load_tokens(email_path):
    tks = []
    file_p = open(email_path)
    email_message = email.message_from_file(file_p)
    [tks.extend(i.split()) for i in email.iterators.body_line_iterator(email_message)]
    file_p.close()
    return tks


def log_probs(email_paths, smoothing):
    total = 0
    dict_words = {}
    dict_final = {}

    for p in email_paths:
        for t in load_tokens(p):

            if t not in dict_words:
                dict_words[t] = 1

            else:
                dict_words[t] += 1
            total += 1

    dlen = len(dict_words.keys())

    other = math.log(smoothing / (total + smoothing * (dlen + 1)))
    dict_final["<UNK>"] = other

    for k, v in dict_words.items():
        num = math.log((dict_words[k] + smoothing) / (total + smoothing * (dlen + 1)))
        dict_final[k] = num

    return dict_final


class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing):

        lst_spam = []
        lst_ham = []

        for i in os.listdir(spam_dir):
            lst_spam.append(spam_dir + "/" + i)

        for i in os.listdir(ham_dir):
            lst_ham.append(ham_dir + "/" + i)

        spamlen = len(lst_spam)
        hamlen = len(lst_ham)
        self.dict_spam = log_probs(lst_spam, smoothing)
        self.dict_ham = log_probs(lst_ham, smoothing)
        self.spam_probability = float(spamlen) / float(spamlen + hamlen)
        self.not_spam_probability = 1 - self.spam_probability

    def is_spam(self, email_path):

        w_dict = {}
        spam, ham = 0, 0
        s_dict = self.dict_spam
        h_dict = self.dict_ham

        for p in load_tokens(email_path):
            if p not in w_dict:
                w_dict[p] = 1
            else:
                w_dict[p] += 1

        for key, value in w_dict.items():
            if key in s_dict and key not in h_dict:
                spam += s_dict[key] * w_dict[key]
            if key not in s_dict and key in h_dict:
                ham += h_dict[key] * w_dict[key]
            if key not in s_dict:
                spam += s_dict["<UNK>"] * w_dict[key]
            if key not in h_dict:
                ham += h_dict["<UNK>"] * w_dict[key]

        s_prob = math.log(self.spam_probability)
        h_prob = math.log(self.not_spam_probability)

        if (s_prob + spam) > (h_prob + ham):
            return True
        else:
            return False

    def most_indicative_spam(self, n):

        spam_dict = {}

        s_dict = self.dict_spam
        h_dict = self.dict_ham

        for key, value in s_dict.items():

            if key in h_dict:
                power_spam = pow(math.e, s_dict[key])
                power_ham = pow(math.e, h_dict[key])

                result_spam = float(power_spam * self.spam_probability)
                result_ham = float(power_ham * self.not_spam_probability)

                v = h_dict[key] - float(math.log(result_spam + result_ham))

                spam_dict[key] = v

        getkeys = spam_dict.keys()
        sorted_keys = sorted(getkeys, key=spam_dict.get)
        solution = sorted_keys[:n]
        return solution

    def most_indicative_ham(self, n):

        ham_dict = {}
        s_dict = self.dict_spam
        h_dict = self.dict_ham

        for key, value in h_dict.items():

            if key in s_dict:
                power_spam = pow(math.e, s_dict[key])
                power_ham = pow(math.e, self.dict_ham[key])

                result_spam = float(power_spam * self.spam_probability)
                result_ham = float(power_ham * self.not_spam_probability)

                v = s_dict[key] - float(math.log(result_spam + result_ham))

                ham_dict[key] = v

        getkeys = ham_dict.keys()
        sorted_keys = sorted(getkeys, key=ham_dict.get)
        solution = sorted_keys[:n]
        return solution

