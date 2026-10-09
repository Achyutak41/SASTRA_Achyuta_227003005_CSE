from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    def encode(
        self,
        texts
    ):
        """
        Convert text into embedding vectors.
        """
        raise NotImplementedError


    @abstractmethod
    def dimension(self):
        """
        Return embedding dimension.
        """
        raise NotImplementedError


    @abstractmethod
    def model_name(self):
        """
        Return actual model identifier.
        """
        raise NotImplementedError