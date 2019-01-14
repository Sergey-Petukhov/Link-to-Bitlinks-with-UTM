# Link to Bitlinks with UTM

Web service for automatic processing of URLs and generating bitlinks.

## The bottom line
There is an Internet project: a website and 3 resources in social networks.
The project team needs to post links to pages in social networks.

## Problems
1. Source links are **very long** — 100-130 characters, they need to be shorten using a third-party service https://bitly.com/, using the project profile.

2. For web analytics purposes, the original links should be changed by adding the necessary **UTM tags** (then it will be possible to determine from which social network the user made the transition).
As a result, for one page of the site you need to create and simplify **3 different links**.

3. 95% of the original links contain other tags that require removal.

4. A large team performs similar actions from a smartphone (**NOT** a hi-end model with small display) with a poor Internet connection and sometimes **disabled JavaScript** (https://bitly.com/ **does not work**).

As a result, the processing of links for **one page takes ~10 minutes**.

## Example:
Original link: https://subdomain.domain.ru/category/page-name-some-id?from=somewhere

It is necessary to remove "from = somewhere": https://subdomain.domain.ru/category/page-name-some-id?

Create 3 links for social networks with the necessary UTM tags:
* https://subdomain.domain.ru/category/page-name-some-id?utm_source=telegram&utm_medium=social&utm_campaign=our-channel
* https://subdomain.domain.ru/category/page-name-some-id?utm_source=vk&utm_medium=social&utm_campaign=our-public
* https://subdomain.domain.ru/category/page-name-some-id?utm_source=instagram&utm_medium=social&utm_campaign=our-profile

Shorting 3 different links using https://bitly.com/, using the project profile:
* http://bit.ly/2QgHMIE
* http://bit.ly/2Vl9gAB
* http://bit.ly/2QgjM8y


## Running a web service for testing
http://35.156.199.247/bitlinks
