from itertools import count, imap, ifilter

def bin_packing(capacity, items):

    N = len(items)
    
    def pack(remainings, step=0):
        amount = items[step]
        left, right = [], list(remainings)
        index = 0
        while right:
            remaining = right.pop(0)
            if amount <= remaining:
                if step + 1 == N:
                    return [(index, amount)]
                result = pack(left + [remaining - amount] + right, step + 1)
                if result:
                    return [(index, amount)] + result
            left.append(remaining)
            index += 1
    
    #m is a lower bound to store all items
    m = sum(items) / capacity + 1
    
    for solution in ifilter(None, imap(pack, imap([capacity].__mul__, count(m)))):
        result = {}
        for i, el in solution:
            if i not in result:
                result[i] = []
            result[i].append(el)
        return result.values()