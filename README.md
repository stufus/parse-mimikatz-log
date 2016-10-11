# Overview

This started out as a quick and dirty tool to parse and organise large amounts of mimikatz output and I wrote it to be able to parse the usual format even when interleaved with other random output.

```
*     Username :
*     Domain :
*     Password :
```

Sometimes mimikatz will generate a huge amount of output; the classic example is running ```sekurlsa::logonpasswords``` on a lsass process dump from an Exchange server. Although there are a few tools to parse this, I wanted something that I could just ```cat`` or pipe in all files in any order and expect it to parse them, ignore any malformed output and offer enough flexibility to allow the credentials to be presented in different forms.

# Compatibility

It works with mimikatz 2.0

# Further work

I shall update it as needed and as new versions of mimikatz come out. It was not a significant piece of work but I hope it is useful to someone.
