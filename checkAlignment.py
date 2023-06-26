import csv
import re
import operator

def minDis(s1, s2, n, m, dp):
    # If any string is empty,
    # return the remaining characters of other string
    if (n == 0):
        return m
    if (m == 0):
        return n

    # To check if the recursive tree
    # for given n & m has already been executed
    if (dp[n][m] != -1):
        return dp[n][m];

    # If characters are equal, execute
    # recursive function for n-1, m-1
    if (s1[n - 1] == s2[m - 1]):
        if (dp[n - 1][m - 1] == -1):
            dp[n][m] = minDis(s1, s2, n - 1, m - 1, dp)
            return dp[n][m]
        else:
            dp[n][m] = dp[n - 1][m - 1]
            return dp[n][m]

    # If characters are nt equal, we need to
    # find the minimum cost out of all 3 operations.
    else:
        if (dp[n - 1][m] != -1):
            m1 = dp[n - 1][m]
        else:
            m1 = minDis(s1, s2, n - 1, m, dp)

        if (dp[n][m - 1] != -1):
            m2 = dp[n][m - 1]
        else:
            m2 = minDis(s1, s2, n, m - 1, dp)
        if (dp[n - 1][m - 1] != -1):
            m3 = dp[n - 1][m - 1]
        else:
            m3 = minDis(s1, s2, n - 1, m - 1, dp)

        dp[n][m] = 1 + min(m1, min(m2, m3))
        return dp[n][m]


def main(file):
    to_prettify = []
    total_res = []
    with open(file, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            en = row[0].strip()
            mt = row[1].strip()
            if "(DONT TRANSLATE)" not in en and "\n" not in en and en.count("[") > 0 and en.count("[") == mt.count("[") and en.count("]") == mt.count("]"):
                en = re.findall(r'\[(.*?)\]', en)
                mt = re.findall(r'\[(.*?)\]', mt)
                for i, element in enumerate(en):
                    en[i] = element.strip()
                for i, element in enumerate(mt):
                    mt[i] = element.strip()
                for i, entity in enumerate(en):
                    # try:
                        # print(entity, mt[i])
                    n = len(entity)
                    if len(mt) <= i:
                        print("")
                    m = len(mt[i])
                    dp = [[-1 for i in range(m + 1)] for j in range(n + 1)]
                    to_prettify.append([entity, mt[i], minDis(entity, mt[i], n, m, dp)])
                    total_res.append(minDis(entity, mt[i], n, m, dp))
                    # except:
                    #     print("ERROR")
    print(sorted(to_prettify, key=operator.itemgetter(2), reverse=True))
    print(Average(total_res))
    print(max(total_res))
    print(min(total_res))
    with open('med.csv', 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(sorted(to_prettify, key=operator.itemgetter(2), reverse=True))
        # for line in sorted(to_prettify, key=operator.itemgetter(2), reverse=True):
        #     f.write("%s\n" % line)
        # f.write(str(Average(total_res)))
        # f.write(str(max(total_res)))
        # f.write(str(min(total_res)))

def Average(lst):
    return sum(lst) / len(lst)
main("nlu.csv")