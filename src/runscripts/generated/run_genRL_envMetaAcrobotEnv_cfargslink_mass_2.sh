#!/bin/bash
#
#SBATCH --mail-user=benjamin@tnt.uni-hannover.de
#SBATCH --mail-type=ALL
#SBATCH --partition=cpu_normal
#SBATCH --job-name=genRL_envMetaAcrobotEnv_cfargslink_mass_2
#SBATCH --output=slurmout/slurm-%j.out
#SBATCH --array=0-4
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2000M



python run_stablebaselines.py --num_contexts 100 --steps 1000000 --add_context_feature_names_to_logdir --hp_file hyperparameter.yml --outdir results/singlecontextfeature_0.1/box2d/MetaAcrobotEnv  --num_workers 1 --default_sample_std_percentage 0.1  --eval_freq 1000 --seed $SLURM_ARRAY_TASK_ID --scale_context_features no --env MetaAcrobotEnv --context_feature_args link_mass_2