# Competitive Programming badges

A simple GitHub-style badge for your competitive programming profile

Currently supports:

- [Codeforces](https://codeforces.com/)
- [TopCoder](https://www.topcoder.com/community/arena)
- [AtCoder](https://atcoder.jp/)

## Usage

The basic endpoint is `https://badges.joonhyung.xyz/[platform]/[handle].svg`.

`[![Codeforces](https://badges.joonhyung.xyz/codeforces/jo_on.svg)](https://codeforces.com/profile/jo_on)`

[![Codeforces](https://badges.joonhyung.xyz/codeforces/jo_on.svg)](https://codeforces.com/profile/jo_on)

`[![TopCoder](https://badges.joonhyung.xyz/topcoder/homology.svg)](https://www.topcoder.com/members/homology)`

[![TopCoder](https://badges.joonhyung.xyz/topcoder/homology.svg)](https://www.topcoder.com/members/homology)

`[![AtCoder](https://badges.joonhyung.xyz/atcoder/topology.svg)](https://atcoder.jp/users/topology)`

[![AtCoder](https://badges.joonhyung.xyz/atcoder/topology.svg)](https://atcoder.jp/users/topology)

You can also further customize your badges using query strings. The following options are supported:

- `left_text`: the text to appear in the left part of the badge; defaults to the name of the platform
- `right_text`: the text to appear in the right part of the badge; defaults to your rating
- `left_link`: the URL to be redirected when the left-hand text is clicked; defaults to the URL of the platform (meaningless if used in GitHub profile)
- `right_link`: the URL to be redirected when the left-hand text is clicked; defaults to the URL of your profile of the platform
- `whole_link`: if `left_link` and `right_link` are not set, the URL to be redirected when the badge is clicked
- `logo`: The base64 or URL of the image; defaults to the logo of the platform
- `left_color`: the background color of the left part of the badge; defaults to #555
- `right_color`: the background color of the right part of the badge; defaults to the color corresponding to your rating
- `whole_title`: the title attribute of the entire badge
- `left_title`: the title attribute of the left part of the badge
- `right_title`: the title attribute of the right part of the badge
- `id_suffix`: the suffix of the id attributes of the elements of the badge

An example:

`[![AtCoder](https://badges.joonhyung.xyz/atcoder/tourist.svg?left_color=lightgray)](https://atcoder.jp/users/tourist)`

[![AtCoder](https://badges.joonhyung.xyz/atcoder/tourist.svg?left_color=lightgray)](https://atcoder.jp/users/tourist)

For more details on these options, see Google [pybadges](https://github.com/google/pybadges). Also, please note that some options are meaningless if used in GitHub profile (e.g. `left_link`, `right_link`, ...).


## Notes

- The server caches some data for better performance, so it may take up to 5 minutes to reflect your rating changes.

