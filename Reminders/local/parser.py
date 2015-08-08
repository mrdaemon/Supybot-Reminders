###
# Copyright (c) 2012, Alexandre Gauthier
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

""" Horribly naive parser for the reminder grammar. """

import re

def tokenize(string):

    # Regular expression to extract blocks
    _recipient = re.compile(r'^(.+?)\s(in|to|about)\b',
                            re.IGNORECASE)
    _time = re.compile(r'\bin\s(\d+\s\b.+?\b)(?:\sto\b|\sabout\b|$)',
                            re.IGNORECASE)
    _message = re.compile(r'\b(?:to|about)\s(.+?)(?:\sin\b|$)',
                            re.IGNORECASE)

    recipientmatch = _recipient.search(string)
    timematch = _time.search(string)
    messagematch = _message.search(string)

    if recipientmatch is None:
        raise ReminderSyntaxError("Remind who?")

    if timematch is None:
        raise ReminderSyntaxError("Remind when?")

    if messagematch is None:
        raise ReminderSyntaxError("Remind what..?")

    # Fetch groups, process further and pack as tokens

    # Construct rough, unvalidated list of usernames, using
    # "and" and "," as delimiters to split on. The further
    # tokenization simplifies the parser's operation.
    recipientdelims = re.compile(r'\b,\sand\b\s|\b,\s|\s\band\b\s',
                                    re.IGNORECASE)
    recipientgroups = recipientmatch.group(1)
    recipientblock = recipientdelims.split(recipientgroups)

    # Time is just split in unavlidated elements. Should contain two,
    # the numerical value and the human readable time unit.
    timegroup = timematch.group(1)
    timeblock = timegroup.split()

    # message block is just kept as-is, as a string.
    # It never really gets processed anyways.
    messageblock = messagematch.group(1)

    return {"recipient": recipientblock,
        "time": timeblock, "message": messageblock }


def parse(sender, inputstr):
    """ Simple parser for reminder syntax, returns properly formatted dict

    Keyword arguments:
        sender -- username who sent the message
        inputstr -- string to parse

    Cheat sheet for dict format:

        +--------------+------------------------------------+
        | key          | value description                  |
        +==============+====================================+
        | destinations | python list of usernames to remind |
        +--------------+------------------------------------+
        | time         | when to remind                     |
        +--------------+------------------------------------+
        | message      | actual message reminder            |
        +--------------+------------------------------------+
    """

    # BTW this may throw ReminderSyntaxError
    tokens = tokenize(inputstr)

    result = []

    result.append(parse_recipients[tokens["recipient"]])



def parse_recipients(sender, recipientlist):
    """ Validate and normalize recipients """

    results = []

    for index, token in enumerate(recipientlist):
        # Normalize "me" to the name of the sender
        if token.lower() == "me":
            token = sender

        # No duplicates allowed
        if token.lower() in results:
            raise ReminderSyntaxError(
                "Duplicate recipient %s at position %d" %
                    (recipientlist[index], index)
                )

        # Nick must be valid
        if not bool(_isvalidnick(token)):
            raise ReminderSyntaxError(
                "Invalid recipient near %s at position %d" %
                    (recipientlist[index], index)
            )

        results.append(token.lower())

    return results


def _isvalidnick(s):
    """ Validates that a string is a valid IRC nickname """

    # According to RFC 2812 and RFC 1459
    validchars = r'[]\`_^{|}'
    nickexpr = r'^[a-z%s][-0-9a-z%s]*$' % (
        re.escape(validchars), re.escape(validchars))

    validnick = re.compile(nickexpr, re.IGNORECASE)

    return bool(validnick.match(s))


class ReminderSyntaxError(Exception):
    pass

#class ReminderSyntaxError(Exception):
    #def __init__(self, tokens, index, message):
        #self.index = index
        #self.msg = message

    #def __str__(self):
        #return ("%s near '%s' in input." % (message, tokens[index]))


