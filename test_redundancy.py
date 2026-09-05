from redundancy import (
    calculate_document_redundancy,
    redundancy_label
)


articles = [

    {
        "text": """
        Artificial intelligence is transforming modern
        workplaces. AI tools are increasingly being used
        to automate repetitive tasks.
        """
    },

    {
        "text": """
        AI is changing workplaces by automating many
        repetitive tasks. Businesses are increasingly
        adopting artificial intelligence tools.
        """
    },

    {
        "text": """
        Football clubs are preparing for the new season.
        Several teams have announced new players.
        """
    }

]


print("=" * 70)
print("NEURALDIGEST — REDUNDANCY TEST")
print("=" * 70)


score = calculate_document_redundancy(
    articles
)


print("\nAverage document similarity:")
print(
    f"{score:.4f}"
)


print("\nRedundancy level:")
print(
    redundancy_label(score)
)


print("\n" + "=" * 70)
print("REDUNDANCY TEST COMPLETED")
print("=" * 70)