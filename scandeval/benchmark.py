'''Fetches an updated list of all Scandinavian models on the HuggingFace Hub'''

import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Union, Dict
from collections import defaultdict
import logging
import json
from pathlib import Path

from .dane import DaneBenchmark
from .ddt_pos import DdtPosBenchmark
from .ddt_dep import DdtDepBenchmark
from .angry_tweets import AngryTweetsBenchmark
from .twitter_sent import TwitterSentBenchmark
from .europarl1 import Europarl1Benchmark
from .europarl2 import Europarl2Benchmark
from .lcc1 import Lcc1Benchmark
from .lcc2 import Lcc2Benchmark
from .dkhate import DkHateBenchmark
from .utils import InvalidBenchmark


logger = logging.getLogger(__name__)


class Benchmark:
    '''Benchmarking all the Scandinavian language models.

    Args
        num_finetunings (int, optional):
            The number of times to finetune each model on. Defaults to 10.
        progress_bar (bool, optional):
            Whether progress bars should be shown. Defaults to True.
        save_results (bool, optional):
            Whether to save the benchmark results to
            'scandeval_benchmark_results.json'. Defaults to False.
        language (str or list of str, optional):
            The language codes of the languages to include in the list. Set
            this to 'all' if all languages (also non-Scandinavian) should
            be considered. Defaults to ['da', 'sv', 'no', 'nb', 'nn', 'is',
            'fo'].
        task (str or list of str, optional):
            The tasks to consider in the list. Set this to 'all' if all
            tasks should be considered. Defaults to 'all'.
        batch_size (int, optional):
            The batch size used to finetune and evaluate the model. This
            value must be among 1, 2, 4, 8, 16 and 32. Defaults to 32.
        evaluate_train (bool, optional):
            Whether to evaluate the training set as well. Defaults to False.
        verbose (bool, optional):
            Whether to output additional output. Defaults to False.
    '''
    def __init__(self,
                 num_finetunings: int = 10,
                 progress_bar: bool = True,
                 save_results: bool = False,
                 language: Union[str, List[str]] = ['da', 'sv', 'no', 'nb',
                                                    'nn', 'is', 'fo'],
                 task: Union[str, List[str]] = 'all',
                 batch_size: int = 32,
                 evaluate_train: bool = False,
                 verbose: bool = False):

        # Set parameters
        self.num_finetunings = num_finetunings
        self.progress_bar = progress_bar
        self.save_results = save_results
        self.language = language
        self.task = task
        self.batch_size = batch_size
        self.evaluate_train = evaluate_train
        self.verbose = verbose

        # Initialise variable storing model lists, so we only have to fetch it
        # once
        self._model_lists = None

        # Initialise variable storing all benchmark results, which will be
        # updated as more models are benchmarked
        self.benchmark_results = defaultdict(dict)

        # Initialise the list of all benchmarks, along with their variable
        # names and the more descriptive names
        params = dict(verbose=verbose,
                      batch_size=batch_size,
                      evaluate_train=evaluate_train)
        self._benchmarks = [
            ('dane', 'DaNE with MISC tags', DaneBenchmark(**params)),
            ('dane-no-misc', 'DaNE without MISC tags',
             DaneBenchmark(include_misc_tags=False, **params)),
            ('ddt-pos', 'the POS part of DDT', DdtPosBenchmark(**params)),
            ('ddt-dep', 'the DEP part of DDT', DdtDepBenchmark(**params)),
            ('angry-tweets', 'Angry Tweets', AngryTweetsBenchmark(**params)),
            ('twitter-sent', 'Twitter Sent', TwitterSentBenchmark(**params)),
            ('dkhate', 'DKHate', DkHateBenchmark(**params)),
            ('europarl1', 'Europarl1', Europarl1Benchmark(**params)),
            ('europarl2', 'Europarl2', Europarl2Benchmark(**params)),
            ('lcc1', 'LCC1', Lcc1Benchmark(**params)),
            ('lcc2', 'LCC2', Lcc2Benchmark(**params))
        ]

        # Set logging level based on verbosity
        if verbose:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
        logger.setLevel(logging_level)

    @staticmethod
    def _get_model_ids(language: Optional[str] = None,
                       task: Optional[str] = None) -> List[str]:
        '''Retrieves all the model IDs in a given language with a given task.

        Args:
            language (str or None):
                The language code of the language to consider. If None then the
                models will not be filtered on language. Defaults to None.
            task (str or None):
                The task to consider. If None then the models will not be
                filtered on task. Defaults to None.

        Returns:
            list of str: The model IDs of the relevant models.
        '''
        url = 'https://huggingface.co/models'
        params = dict()
        if language is not None:
            params['filter'] = language
        if task is not None:
            params['pipeline_tag'] = task
        html = requests.get(url, params=params).text
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article')
        model_ids = [header['title']
                     for article in articles
                     for header in article.find_all('header')
                     if header.get('class') is not None and
                     header.get('title') is not None and
                     'items-center' in header['class']]
        return model_ids

    def _get_model_lists(self,
                         languages: List[str],
                         tasks: List[str]) -> Dict[str, List[str]]:
        '''Fetches up-to-date model lists.

        Args:
            languages (list of either str or None):
                The language codes of the language to consider. If None is
                present in the list then the models will not be filtered on
                language.
            tasks (list of either str or None):
                The task to consider. If None is present in the list then the
                models will not be filtered on task.

        Returns:
            dict:
                The keys are filterings of the list, which includes all
                language codes, including 'multilingual', all tasks, as well as
                'all'. The values are lists of model IDs.
        '''
        # Log fetching message
        log_msg = 'Fetching list of models'
        if None not in languages:
            log_msg += f' for the languages {languages}'
            if None not in tasks:
                log_msg += f' and tasks {tasks}'
        else:
            if None not in tasks:
                log_msg += f' for the tasks {tasks}'
        log_msg += ' from the HuggingFace Hub.'
        logger.info(log_msg)

        # Initialise model lists
        model_lists = defaultdict(list)
        for language in languages:
            for task in tasks:
                model_ids = self._get_model_ids(language, task)
                model_lists['all'].extend(model_ids)
                model_lists[language].extend(model_ids)
                model_lists[task].extend(model_ids)

        # Add multilingual models manually
        multilingual_models = ['xlm-roberta-base', 'xlm-roberta-large']
        model_lists['all'].extend(multilingual_models)
        model_lists['multilingual'] = multilingual_models

        # Remove duplicates from the lists
        for lang, model_list in model_lists.items():
            model_lists[lang] = list(set(model_list))

        return model_lists

    def __call__(self,
                 model_id: Optional[Union[List[str], str]] = None,
                 dataset: Optional[Union[List[str], str]] = None,
                 num_finetunings: Optional[int] = None,
                 progress_bar: Optional[bool] = None,
                 save_results: Optional[bool] = None,
                 language: Optional[Union[str, List[str]]] = None,
                 task: Optional[Union[str, List[str]]] = None,
                 batch_size: Optional[int] = None,
                 evaluate_train: Optional[bool] = None,
                 verbose: Optional[bool] = None) -> Dict[str, Dict[str, dict]]:
        '''Benchmarks all models in the model list.

        Args:
            model_id (str, list of str or None, optional):
                The model ID(s) of the models to benchmark. If None then all
                relevant model IDs will be benchmarked. Defaults to None.
            dataset (str, list of str or None, optional):
                The datasets to benchmark on. If None then all datasets will
                be benchmarked. Defaults to None.
            num_finetunings (int or None, optional):
                The number of times to finetune each model on. If None then the
                default value from the constructor will be used. Defaults to
                None.
            progress_bar (bool or None, optional):
                Whether progress bars should be shown. If None then the default
                value from the constructor will be used. Defaults to None.
            save_results (bool or None, optional):
                Whether to save the benchmark results to
                'scandeval_benchmark_results.json'. If None then the default
                value from the constructor will be used. Defaults to None.
            language (str, list of str or None, optional):
                The language codes of the languages to include in the list. Set
                this to 'all' if all languages (also non-Scandinavian) should
                be considered. If None then the default value from the
                constructor will be used. Defaults to None.
            task (str, list of str or None, optional):
                The tasks to consider in the list. Set this to 'all' if all
                tasks should be considered. If None then the default value from
                the constructor will be used. Defaults to None.
            batch_size (int or None, optional):
                The batch size used to finetune and evaluate the model. This
                value must be among 1, 2, 4, 8, 16 and 32. If None then the
                default value from the constructor will be used. Defaults to
                None.
            evaluate_train (bool or None, optional):
                Whether to evaluate the training set as well. If None then the
                default value from the constructor will be used. Defaults to
                None.
            verbose (bool or None, optional):
                Whether to output additional output. If None then the default
                value from the constructor will be used. Defaults to None.

        Returns:
            dict:
                A nested dictionary of the benchmark results. The keys are the
                names of the datasets, with values being new dictionaries
                having the model IDs as keys.
        '''
        # Set default values if the arguments are not set
        if num_finetunings is None:
            num_finetunings = self.num_finetunings
        if progress_bar is None:
            progress_bar = self.progress_bar
        if save_results is None:
            save_results = self.save_results
        if language is None:
            language = self.language
        if task is None:
            task = self.task
        if batch_size is None:
            batch_size = self.batch_size
        if evaluate_train is None:
            evaluate_train = self.evaluate_train
        if verbose is None:
            verbose = self.verbose

        # Ensure that `language` is a list
        if language == 'all':
            languages = [None]
        elif isinstance(language, str):
            languages = [language]
        else:
            languages = language

        # Ensure that `task` is a list
        if task == 'all':
            tasks = [None]
        elif isinstance(task, str):
            tasks = [task]
        else:
            tasks = task

        # If `model_id` is not specified, then fetch all the relevant model IDs
        if model_id is None:

            # If the model lists have not been fetched already, then do it
            if self._model_lists is None:
                self._model_lists = self._get_model_lists(languages=languages,
                                                          tasks=tasks)
            try:
                model_ids = list()
                for language in languages:
                    model_ids.extend(self._model_lists[language])
                for task in tasks:
                    model_ids.extend(self._model_lists[task])
                model_ids.extend(self._model_lists['multilingual'])

            # If the model list corresponding to the language or task was not
            # present in the stored model lists, then fetch new model lists and
            # try again
            except KeyError:
                self._model_lists = self._get_model_lists(languages=languages,
                                                          tasks=tasks)
                model_ids = list()
                for language in languages:
                    model_ids.extend(self._model_lists[language])
                for task in tasks:
                    model_ids.extend(self._model_lists[task])
                model_ids.extend(self._model_lists['multilingual'])

        # Define `model_ids` variable, storing all the relevant model IDs
        elif isinstance(model_id, str):
            model_ids = [model_id]
        else:
            model_ids = model_id

        # Define `datasets` variable, storing all the relevant datasets
        if dataset is None:
            datasets = [d for d, _, _ in self._benchmarks]
        elif isinstance(dataset, str):
            datasets = [dataset]
        else:
            datasets = dataset

        # Fetch the benchmark datasets, filtered by the `datasets` variable
        benchmarks = [(dataset, alias, cls)
                      for dataset, alias, cls in self._benchmarks
                      if dataset in datasets]

        # Benchmark all the models in `model_ids` on all the datasets in
        # `benchmarks`
        for dataset, alias, cls in benchmarks:
            for model_id in model_ids:
                logger.info(f'Benchmarking {model_id} on {alias}:')
                try:
                    params = dict(num_finetunings=num_finetunings,
                                  progress_bar=progress_bar)
                    results = cls(model_id, **params)
                    self.benchmark_results[dataset][model_id] = results
                    logger.debug(f'Results:\n{results}')
                except InvalidBenchmark as e:
                    logger.info(f'{model_id} could not be benchmarked '
                                f'on {alias}. Skipping.')
                    logger.debug(f'The error message was {e}.')

        # Save the benchmark results
        if save_results:
            output_path = Path.cwd() / 'scandeval_benchmark_results.json'
            with output_path.open('w') as f:
                json.dump(self.benchmark_results, f)

        return self.benchmark_results
