class Parser:
    def __new__(self, args: str = None):
        r = {}
        if args is None:
            r['status'] = None
        else:
            r['status'] = True
            if len(args.split(' ')) == 1:
                r = {
                    0: args
                }
            else:
                r = {0: args.split(' ')[0]}
                for each in args.split(' '):
                    if each.startswith('-'):
                        r[each] = args.split(' ')\
                            [list(args.split(' ')).index(each)+1]
        return r