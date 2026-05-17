import os
import openai
import chromadb
os.environ["OPENAI_API_KEY"] = "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"


java_knowledge = [
    "Q: How do strings compare in Java? What is == vs equals?\nA: == checks reference equality meaning same memory address. .equals() checks value equality meaning same content. Always use .equals() for String comparison. Example: 'hello'.equals('hello') is always true but == can be false.",

    "Q: What is NullPointerException and how do you avoid it?\nA: NPE happens when you call a method on a null object reference. Avoid it with null checks using if(obj != null), use Optional<T> to wrap values that might be null, or use Objects.requireNonNull() to fail fast with a clear message.",

    "Q: What is the difference between ArrayList and LinkedList?\nA: ArrayList uses a dynamic array internally, gives O(1) random access by index, but slow O(n) insert and delete in the middle. LinkedList uses doubly linked nodes, gives O(1) insert and delete, but slow O(n) random access. Use ArrayList for most cases unless you insert or delete frequently in the middle.",

    "Q: What are the four pillars of OOP?\nA: Encapsulation means hiding internal data behind methods. Inheritance means a child class extends a parent class and reuses its code. Polymorphism means the same method name behaves differently based on the object. Abstraction means hiding complex implementation and showing only what is necessary.",

    "Q: What is a HashMap and how does it work internally?\nA: HashMap stores key-value pairs. Internally it uses an array of buckets. It calls hashCode() on the key to find the bucket index, then uses equals() to handle collisions in the same bucket. Default capacity is 16 and load factor is 0.75, meaning it resizes when 75% full.",

    "Q: What is the difference between abstract class and interface?\nA: Abstract class can have state, constructors, and method bodies. A class can only extend one abstract class. Interface is a pure contract with no state, and a class can implement multiple interfaces. Use interface when you want to define capability. Use abstract class when you want to share base implementation.",

    "Q: What is garbage collection in Java?\nA: Garbage collection is the JVM automatically freeing memory occupied by objects that are no longer reachable. You cannot force it but can suggest it with System.gc(). The GC runs in the background and uses algorithms like mark-and-sweep to identify and remove unused objects.",

    "Q: What is the volatile keyword in Java?\nA: volatile is a keyword that ensures a variable's value is always read from and written to main memory, not from a thread's local CPU cache. This makes changes to the variable immediately visible to all threads. Use it for simple flags shared between threads. It is lighter than synchronized but only works for single variable visibility.",

    "Q: What is the difference between checked and unchecked exceptions?\nA: Checked exceptions are checked at compile time and must be declared with throws or caught in a try-catch block. Example is IOException. Unchecked exceptions extend RuntimeException and do not need to be declared. Example is NullPointerException and IllegalArgumentException.",

    "Q: What is the Java Stream API?\nA: Stream API introduced in Java 8 allows functional-style processing of collections. You can use filter() to select elements, map() to transform them, reduce() to combine them, and collect() to gather results. Streams are lazy meaning they only process elements when a terminal operation is called. They can also run in parallel with parallelStream().",
]

client     = openai.OpenAI()
chroma     = chromadb.Client()
collection = chroma.create_collection("java_qa")

def embed(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

vectors = embed(java_knowledge)
collection.add(
    documents=java_knowledge,
    embeddings=vectors,
    ids=[str(i) for i in range(len(java_knowledge))]
)


def ask(question):
    # R — Retrieve
    q_vector = embed([question])[0]
    results  = collection.query(query_embeddings=[q_vector], n_results=10)

      # check how good the match is
    best_distance = results["distances"][0][0]
    print(f"[DEBUG] Best match distance: {best_distance:.3f}")
    
    if best_distance > 0.6:
        return "I don't have enough relevant information to answer that."
    
    context = "\n---\n".join(results["documents"][0])
    # rest stays same...

    # A + G — Augment + Generate
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer ONLY from context. If not there, say so."},
            {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

while True:
    q = input("You: ")
    if q.lower() == "quit":
        break
    print(f"\nBot: {ask(q)}\n")