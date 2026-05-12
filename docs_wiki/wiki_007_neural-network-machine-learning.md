# Neural network (machine learning)

Source: https://en.wikipedia.org/wiki/Neural_network_(machine_learning)

In machine learning, a neural network (NN) or neural net, also known as an artificial neural network (ANN), is a computational model inspired by the structure and functions of biological neural networks.
A neural network consists of connected units or nodes called artificial neurons, which loosely model the neurons in the brain. Artificial neuron models that mimic biological neurons more closely have also been recently investigated and shown to significantly improve performance. These are connected by edges, which model the synapses in the brain. Each artificial neuron receives signals from connected neurons, then processes them and sends a signal to other connected neurons. The "signal" is a real number, and the output of each neuron is computed by some non-linear function of the totality of its inputs, called the activation function. The strength of the signal at each connection is determined by a weight, which adjusts during the learning process.
Typically, neurons are aggregated into layers. Different layers may perform different transformations on their inputs. Signals travel from the first layer (the input layer) to the last layer (the output layer), possibly passing through multiple intermediate layers (hidden layers). A network is typically called a deep neural network if it has at least two hidden layers.
Advances in computing power, particularly the use of graphics processing units (GPUs), and the availability of large datasets further accelerated neural network research in the early 21st century. These developments enabled the training of deep neural networks capable of learning hierarchical representations from complex data.
Architectural innovations such as convolutional neural networks (CNNs) significantly improved performance in computer vision tasks, while recurrent neural networks (RNNs) enabled modeling of sequential data such as speech and time-series information. More recently, transformer architectures introduced attention mechanisms that allow neural networks to model long-range dependencies in data and have become foundational for modern large language models.
Today, artificial neural networks are used for various tasks, including predictive modeling, adaptive control, and solving problems in artificial intelligence.


== History ==


=== Mathematical foundations ===
Today's deep neural networks are based on early work in statistics over 200 years ago. The simplest kind of feedforward neural network (FNN) is a linear network, which consists of a single layer of output nodes with linear activation functions; the inputs are fed directly to the outputs via a series of weights. The sum of the products of the weights and the inputs is calculated at each node. The mean squared errors between these calculated outputs and the given target values are minimized by creating an adjustment to the weights. This technique has been known for over two centuries as the method of least squares or linear regression. It was used as a means of finding a good rough linear fit to a set of points by Legendre (1805) and Gauss (1795) for the prediction of planetary movement.


=== Perceptrons ===
Historically, digital computers such as the von Neumann model operate via the execution of explicit instructions with access to memory by a number of processors. Some neural networks, on the other hand, originated from efforts to model information processing in biological systems through the framework of connectionism. Unlike the von Neumann model, connectionist computing does not separate memory and processing.
Warren McCulloch and Walter Pitts (1943) considered a non-learning computational model for neural networks. This model paved the way for research to split into two approaches; one approach focused on biological processes while the other focused on the application of neural networks to artificial intelligence. McCulloch and Pitts also developed mathematical models of artificial neurons capable of representing logical functions.
In
