# Quantum machine learning

Source: https://en.wikipedia.org/wiki/Quantum_machine_learning

Quantum machine learning (QML) is the study of quantum algorithms for machine learning. It often refers to quantum algorithms for machine learning tasks which analyze classical data, sometimes called quantum-enhanced machine learning.
QML algorithms use qubits and quantum operations to try to improve the space and time complexity of classical machine learning algorithms. Hybrid QML methods involve both classical and quantum processing, where computationally difficult subroutines are outsourced to a quantum device. These routines can be more complex in nature and executed faster on a quantum computer. Furthermore, quantum algorithms can be used to analyze quantum states instead of classical data.
The term "quantum machine learning" is sometimes used to refer classical machine learning methods applied to data generated from quantum experiments (i.e. machine learning of quantum systems), such as learning the phase transitions of a quantum system or creating new quantum experiments.
QML also extends to a branch of research that explores methodological and structural similarities between certain physical systems and learning systems, in particular neural networks. For example, some mathematical and numerical techniques from quantum physics are applicable to classical deep learning and vice versa.
Furthermore, researchers investigate more abstract notions of learning theory with respect to quantum information, sometimes referred to as "quantum learning theory".


== Machine learning with quantum computers ==
Quantum-enhanced machine learning refers to quantum algorithms that solve tasks in machine learning, thereby improving and often expediting classical machine learning techniques. Such algorithms typically require one to encode the given classical data set into a quantum computer to make it accessible for quantum information processing. Subsequently, quantum information processing routines are applied and the result of the quantum computation is read out by measuring the quantum system. For example, the outcome of the measurement of a qubit reveals the result of a binary classification task. While many proposals of QML algorithms are still purely theoretical and require a full-scale universal quantum computer to be tested, others have been implemented on small-scale or special purpose quantum devices.


=== Quantum associative memories and quantum pattern recognition ===
Early work on quantum associative memories has been done by Dan Ventura and Tony Martinez and by Carlo A. Trugenberger in the late 1990s and early 2000s. 
Associative (or content-addressable) memories are able to recognize stored content on the basis of a similarity measure, while random access memories are accessed by the address of stored information and not its content. As such they must be able to retrieve both incomplete and corrupted patterns, the essential machine learning task of pattern recognition.
Typical classical associative memories store p patterns in the 
  
    
      
        O
        (
        
          n
          
            2
          
        
        )
      
    
    {\displaystyle O(n^{2})}
  
 interactions (synapses) of a real,  symmetric energy matrix over a network of n artificial neurons. The encoding is such that the desired patterns are local minima of the energy functional and retrieval is done by minimizing the total energy, starting from an initial configuration.
Unfortunately, classical associative memories are severely limited by the phenomenon of cross-talk. When too many patterns are stored, spurious memories appear which quickly proliferate, so that the energy landscape becomes disordered and no retrieval is anymore possible. The number of storable patterns is typically limited by a linear function of the number of neurons, 
  
    
      
        p
        ≤
        O
        (
        n
        )
      
    
    {\displaystyle p\leq O(n)}
  
.
Quantum associative memories (in their simplest realization) store patterns
