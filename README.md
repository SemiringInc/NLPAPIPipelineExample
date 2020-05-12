# NLP API Pipeline Example

An example NLP pipeline in Python using [spaCy], [Neuralcoref], and [Benepar]

(C) 2020 by [Semiring] Inc., [Damir Cavar] <damir@semiring.inc>


The pipeline code is licensed under the Apache License Version 2.0. See LICENSE.txt for License details. For [spaCy], [Benepar], and [Neuralcoref] consult their license information.


This is a basic wrapper for different NLP components and pipelines to output a [JSON-NLP] annotation for a given raw text input.



## Installation

To be able to run this [Flask] or RESTful server, you need to install the required Python modules using the following command:

   pip install -r requirements.txt

In the command above, if your operating system provides Python 2 and Python 3, the pip command might have to be *pip3*.

It might be more problematic to install the compatible [Benepar] and [Neuralcoref] module on your platform.


### Install Benepar

Here is how one might installed [Benepar]:

- Make sure you have a running Python 3.7.x and some C++ compiler (on Windows one might use [Visual Studio C++ Community](https://visualstudio.microsoft.com/vs/community/) and also install CMake via [Chocolatey], etc.)
- Make sure you have Cython installed: *pip install -U cython*
- Make sure that you have the newest Tensorflow set up (see the website of tensorflow for your Python, required up to recently was Python 3.7.x and not supported was 3.8.x!)
- Use the [Benepar] code from our shared Box folder: self-attentive-parser.zip
- Unpack the self-attentive-parser.zip on your computer and in a command line interface change into this folder
- run the following command:

   python setup.py install

You might need to use *python3* depending on your system. You might need to say "./setup.py" on Linux or ".\setup.py" on Windows.

If this worked, [install the language models for spaCy](https://spacy.io/usage/models), [Benepar](https://pypi.org/project/benepar/), and [Neuralcoref](https://github.com/huggingface/neuralcoref).

In the command line of your account, that is not the Admin or root account, load python and run the following commands in the interactive Python interpreter:

   import benepar
   benepar.download('benepar_en2')



### Install Neuralcoref

Do not install Neuralcoref using *pip*. If you did, use:

   pip uninstall neuralcoref

to remove it. Clone the Neuralcoref GitHub repo to your local drive. Change in a command line into the cloned folder *neuralcoref* and just install using:

   pip setup.py install



## Server

To run the server on your local machine, simply run *test.py*:

   python test.py

You can interact now with the server by calling it in the Firefox browser window using for example:

   http://localhost:9002/?text=John%20loves%20Mary.

or with just white space instead of %20 in the URL line of the browser:

   http://localhost:9002/?text=John loves Mary.

To stop the server, press Ctrl-C in the terminal window.

You can change the port in the *config.ini* file.


## Testing the Server

Use some tool like Postman for POST requests, or your browser for GET requests as described above, or the CURL scripts in the code base here.

If you do not have CURL on your Windows machine, use [Chocolatey] or some other approach to install it.


## JSON-NLP

The [JSON-NLP] is maintained by [Semiring] Inc., and the Schema with example code is available on GitHub.



[Semiring]: https://semiring.com/ "Semiring Inc."
[Damir Cavar]: http://damir.cavar.me/ "Damir Cavar"
[JSON-NLP]: https://github.com/SemiringInc/JSON-NLP "JSON-NLP"
[Flask]: https://palletsprojects.com/p/flask/ "Flask"
[Benepar]: https://github.com/nikitakit/self-attentive-parser "Benepar"
[Neuralcoref]: https://github.com/huggingface/neuralcoref "Neuralcoref"
[Chocolatey]: https://chocolatey.org/ "Chocolatey"
