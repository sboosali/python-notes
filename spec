operators
eg "x -> y"

whitespace grouping
eg   5  /  1*2 + 3*4   ==   5/((1*2)+(3*4))
implement. "." " . " "  .  " ... (works if operators aren't adjacent)
implement. preprocess, find max num spaces, put parens on either side of the most-spaced operator, recur

chaining operators
eg "_ -> _ -> ..."
~ ∞-ary operator with same operator

n-ary operators
eg "_ < _ where _"
eg "_ ~ _ as _ ~ _"

head prefixing
eg
x
-> y
