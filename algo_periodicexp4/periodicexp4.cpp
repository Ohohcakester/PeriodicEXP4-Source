//#define ENABLE_LOGGING
//#define MODE_NORMALIZE
#define MODE_APPROXIMATE
#define MODE_STABLE


#ifndef MODE_STABLE
#define MODE_NOT_STABLE
#endif

#ifndef MODE_APPROXIMATE
#define MODE_NOT_APPROXIMATE
#endif

#ifdef MODE_APPROXIMATE
#undef MODE_NORMALIZE
#undef MODE_STABLE
#undef MODE_NOT_STABLE
#endif

#include <iostream>
#include <vector>
#include <cmath>
#include <random>
const double MIN_DOUBLE = std::numeric_limits<double>::min();
const double MAX_DOUBLE = std::numeric_limits<double>::max();

class DataLog {
public:
    int cols;
    int index;
    std::vector<double> data;
    DataLog(int cols): cols(cols), index(0) {}
    void add(double v) { data.push_back(v); }
    void reset() { index = 0; }
    void clear() { data.clear(); reset(); }
    double next() { return data[index++]; }
};

class PeriodicExp4 {
public:
    DataLog* dataLog;
private:
    // Data
    // INDEX: [f][label][arm]
    std::vector<std::vector<std::vector<double> > > w; // weight

#ifdef MODE_APPROXIMATE
    std::vector<std::vector<double> > mw; // max(w) over all arms    
#endif

#ifdef MODE_NOT_APPROXIMATE
    std::vector<std::vector<std::vector<double> > > b; // expweight

    // INDEX: [f][label]
    std::vector<std::vector<double> > sb; // sum(b) over all arms

# ifdef MODE_NOT_STABLE
    // INDEX: [f]
    std::vector<double> bf; // product of sb over all labels
# endif
#endif

    // INDEX: [K]
    std::vector<double> p;

    // Results
    int chosenArm;
    std::vector<int> currentLabels; // indexed by partition F

    // Random
    std::mt19937 gen;
    std::uniform_real_distribution<double> dis;

    int T;
    int K;
    int F;
    double gamma;
    std::vector<int> nLabels;

    int normalizeCooldown;


private:

#ifdef MODE_APPROXIMATE
    const double computeLogSumExp(const std::vector<double>& values) {
        double max = 0;
        for (size_t i=0; i<values.size(); ++i) {
            if (values[i] > max) max = values[i];
        }
        return max;
    }
#endif

#ifdef MODE_APPROXIMATE
    std::vector<double> temp_mwf;
    std::vector<double> temp_mwf_i;

    void computeWithNewLabels() {
        temp_mwf.resize(F);
        temp_mwf_i.resize(F);

        for (size_t f=0; f<F; ++f) {
            double mwf = 0;
            for (size_t l=0; l<nLabels[f]; ++l) {
                if (l == currentLabels[f]) continue;
                mwf += mw[f][l];
            }
            temp_mwf[f] = mwf;
        }

        double smallestWeight = MAX_DOUBLE;
        for (size_t i=0; i<K; ++i) {
            for (size_t f=0; f<F; ++f) {
                temp_mwf_i[f] = w[f][currentLabels[f]][i] + temp_mwf[f];
            }
            double armWeight = computeLogSumExp(temp_mwf_i);
            p[i] = armWeight;
            if (armWeight < smallestWeight) smallestWeight = armWeight;
        }
        double totalR = 0;
        for (size_t i=0; i<K; ++i) {
            // std::min(?, 700.0) because running std::exp on values above 700 can produce inf
            p[i] = std::exp(std::min(p[i]-smallestWeight,700.0));
            totalR += p[i];
        }

        for (size_t i=0; i<K; ++i) {
            p[i] /= totalR;
        }
    }
#endif

#ifdef MODE_STABLE
    std::vector<float> temp_bff;

    void computeWithNewLabels() {
        temp_bff.resize(F);

        for (size_t f=0; f<F; ++f) {
            double bff = 1;
            for (size_t l=0; l<nLabels[f]; ++l) {
                if (l == currentLabels[f]) continue;
                bff *= sb[f][l];
            }
            temp_bff[f] = std::max(MIN_DOUBLE, bff);
        }

        double totalR = 0;
        for (size_t i=0; i<K; ++i) {
            double sum = 0;
            for (size_t f=0; f<F; ++f) {
                sum += b[f][currentLabels[f]][i] * temp_bff[f];
            }
            sum = std::max(MIN_DOUBLE, sum);

            p[i] = sum;
            totalR += sum;
        }

        for (size_t i=0; i<K; ++i) {
            p[i] /= totalR;
        }
    }
#endif

#ifdef MODE_NOT_STABLE
    void computeWithNewLabels() {
        double totalR = 0;

        for (size_t i=0; i<K; ++i) {
            double sum = 0;
            for (size_t f=0; f<F; ++f) {
                sum += b[f][currentLabels[f]][i] * bf[f] / sb[f][currentLabels[f]];
            }

            p[i] = sum;
            totalR += sum;
        }

        for (size_t i=0; i<K; ++i) {
            p[i] /= totalR;
        }
    }
#endif

    void normalize() {
        /*if (normalizeCooldown > 0) {
            --normalizeCooldown;
            return;
        }
        // amortizing the number of normalizations.
        normalizeCooldown = 0;
        for (size_t f=0; f<F; ++f) {
            normalizeCooldown += K*nLabels[f];
        }*/


        double adjustment = 0;
        const double MAX_W = 1;

        for (size_t f=0; f<F; ++f) {
            const int labelCount = nLabels[f];
            for (size_t l=0; l<labelCount; ++l) {
                for (size_t i=0; i<K; ++i) {
                    double requiredSubtraction = labelCount*(w[f][l][i] - MAX_W);
                    if (requiredSubtraction > adjustment) {
                        adjustment = requiredSubtraction;
                    }
                }
            }
        }
        if (adjustment > 0) {
            for (size_t f=0; f<F; ++f) {
                const int labelCount = nLabels[f];
                for (size_t l=0; l<labelCount; ++l) {
                    for (size_t i=0; i<K; ++i) {
                        w[f][l][i] -= adjustment/labelCount;
#ifdef MODE_NOT_APPROXIMATE
                        b[f][l][i] = std::exp(w[f][l][i]);
#endif
                    }

#ifdef MODE_APPROXIMATE
                    // update relevant mw
                    mw[f][l] = computeMaxw(f, l);
#endif
#ifdef MODE_NOT_APPROXIMATE
                    // update relevant sb
                    sb[f][l] = std::max(MIN_DOUBLE, computeSumb(f, l));
#endif
                }
            }
        }
    }

    void computeWithPreviousLabels(double reward) {

        for (size_t f=0; f<F; ++f) {
            const int label = currentLabels[f];
            w[f][label][chosenArm] += reward * gamma / K / p[chosenArm];
        }

#ifdef MODE_NORMALIZE
        normalize();
#endif

        for (size_t f=0; f<F; ++f) {
            const int label = currentLabels[f];

#ifdef MODE_NOT_APPROXIMATE
            b[f][label][chosenArm] = std::exp(w[f][label][chosenArm]);
#endif

#ifdef MODE_APPROXIMATE
            mw[f][label] = computeMaxw(f, label);
#endif

#ifdef MODE_NOT_STABLE
            // update relevant bf - Part 1
            bf[f] /= sb[f][label];
            // update relevant sb
            sb[f][label] = computeSumb(f, label);
            // update relevant bf - Part 2
            bf[f] *= sb[f][label];
#endif

#ifdef MODE_STABLE
            // update relevant sb
            sb[f][label] = std::max(MIN_DOUBLE, computeSumb(f, label));
#endif
        }
    }

#ifdef MODE_APPROXIMATE
    const double computeMaxw(size_t f, int label) {
        const std::vector<double>& vec = w[f][label];
        return computeLogSumExp(vec);
    }
#endif

#ifdef MODE_NOT_APPROXIMATE
    const double computeSumb(size_t f, int label) {
        const std::vector<double>& vec = b[f][label];
        double sum = 0;
        for (size_t i=0; i<K; ++i) {
            sum += vec[i];
        }
        return sum;
    }
#endif

    // computes nextArm based on the existing probabilities
    void decideNextArm() {
        double v = dis(gen);
        chosenArm = 0;
        while (v > p[chosenArm]) {
            v -= p[chosenArm];
            ++chosenArm;
        }
        if (chosenArm >= K) chosenArm = K-1;
    }

public:
    // To use a default value of gamma, set gamma to -1.
    PeriodicExp4(int _T, int _K, int _F, int* labelCounts, int seed, double _gamma): T(_T), K(_K), F(_F), dis(0.0, 1.0), gen(seed), gamma(_gamma) {
        dataLog = new DataLog(1);
        normalizeCooldown = 0;

        // Set gamma if not yet set.
        if (gamma < 0) {
            double N = 0;
            for (size_t i=0; i<F; ++i) {
                N += pow(K,labelCounts[i]);
            }
            gamma = sqrt(K * std::log(N) / T);
        }

        currentLabels.resize(F);

        nLabels.resize(F);
        w.resize(F);
#ifdef MODE_APPROXIMATE        
        mw.resize(F);
#endif
#ifdef MODE_NOT_APPROXIMATE
        b.resize(F);
        sb.resize(F);
#endif
#ifdef MODE_NOT_STABLE        
        bf.resize(F);
#endif        
        for (size_t f=0; f<F; ++f) {
            const int labelCount = labelCounts[f];
            nLabels[f] = labelCount;

#ifdef MODE_APPROXIMATE     
            w[f].resize(labelCount);
            mw[f].resize(labelCount);
            for (size_t l=0; l<nLabels[f]; ++l) {
                w[f][l].resize(K);
                for (size_t i=0; i<K; ++i) {
                    w[f][l][i] = 0;
                }
                mw[f][l] = 0;
            }
#endif

#ifdef MODE_NOT_APPROXIMATE
            w[f].resize(labelCount);
            b[f].resize(labelCount);
            sb[f].resize(labelCount);
            for (size_t l=0; l<nLabels[f]; ++l) {
                w[f][l].resize(K);
                b[f][l].resize(K);
                for (size_t i=0; i<K; ++i) {
                    w[f][l][i] = 0;
                    b[f][l][i] = 1;
                }
                sb[f][l] = K;
            }
#endif
#ifdef MODE_NOT_STABLE
            //bf[f] = pow(K,labelCount);
            bf[f] = 1;
#endif
        }

        p.resize(K);
        for (size_t i=0; i<K; ++i) {
            p[i] = 1.0f/K;
        }

        // IDEA:::: REPEAT MANy OF THE FUNCTIONS FOR WEIGHTING??
    }

    int getNextArm(int* labels) {
        for (size_t f=0; f<F; ++f) {
            currentLabels[f] = labels[f];
        }
        computeWithNewLabels();
        decideNextArm();
        return chosenArm;
    }

    // inputs the reward for arm nextArm on the current timestep t.
    void giveReward(double reward, double _gamma) {
        if (_gamma > 0) this->gamma = _gamma;
        computeWithPreviousLabels(reward);
    }

    DataLog* getCurrentTimestepData() {
        dataLog->clear();

#ifdef MODE_APPROXIMATE
        temp_mwf.resize(F);

        for (size_t f=0; f<F; ++f) {
            double mwf = 0;
            for (size_t l=0; l<nLabels[f]; ++l) {
                if (l == currentLabels[f]) continue;
                mwf += mw[f][l];
            }
            temp_mwf[f] = mwf;
        }

        // 1. weight of each partition function
        for (size_t f=0; f<F; ++f) {
            dataLog->add(temp_mwf[f]+mw[f][currentLabels[f]]);
        }

        // 2. weight of each arm
        for (size_t i=0; i<K; ++i) {
            double largest = 0;
            for (size_t f=0; f<F; ++f) {
                double functionWeight = w[f][currentLabels[f]][i] + temp_mwf[f];
                if (functionWeight > largest) largest = functionWeight;
            }
            dataLog->add(largest);
        }
#endif

#ifdef MODE_NOT_STABLE
        // 1. weight of each partition function
        for (size_t f=0; f<F; ++f) {
            dataLog->add(bf[f]);
        }

        // 2. weight of each arm
        for (size_t i=0; i<K; ++i) {
            double weight = 0;
            for (size_t f=0; f<F; ++f) {
                weight += b[f][currentLabels[f]][i] * bf[f] / sb[f][currentLabels[f]];
            }
            dataLog->add(weight);
        }
#endif

#ifdef MODE_STABLE
        temp_bff.resize(F);
        for (size_t f=0; f<F; ++f) {
            double bff = 1;
            for (size_t l=0; l<nLabels[f]; ++l) {
                if (l == currentLabels[f]) continue;
                bff *= sb[f][l];
            }
            temp_bff[f] = bff;
        }

        // 1. weight of each partition function
        for (size_t f=0; f<F; ++f) {
            dataLog->add(temp_bff[f]*sb[f][currentLabels[f]]);
        }

        // 2. weight of each arm
        for (size_t i=0; i<K; ++i) {
            double weight = 0;
            for (size_t f=0; f<F; ++f) {
                weight += b[f][currentLabels[f]][i] * temp_bff[f];
            }
            dataLog->add(weight);
        }
#endif

        // 3. probability of each arm
        for (size_t i=0; i<K; ++i) {
            dataLog->add(p[i]);
        }
        return dataLog;
    }
};

extern "C" {
    PeriodicExp4* PeriodicExp4_new(int T, int K, int F, int* labelCounts, int seed){ return new PeriodicExp4(T,K,F,labelCounts,seed,-1); }
    PeriodicExp4* PeriodicExp4_new_g(int T, int K, int F, int* labelCounts, int seed, double gamma){ return new PeriodicExp4(T,K,F,labelCounts,seed,gamma); }
    int PeriodicExp4_getNextArm(PeriodicExp4* obj, int* labels) { return obj->getNextArm(labels); }
    void PeriodicExp4_giveReward(PeriodicExp4* obj, double reward, double _gamma) { obj->giveReward(reward, _gamma); }
    DataLog* PeriodicExp4_getLog(PeriodicExp4* obj){ return obj->dataLog; }
    DataLog* PeriodicExp4_getCurrentTimestepData(PeriodicExp4* obj){ return obj->getCurrentTimestepData(); }
    void DataLog_reset(DataLog* obj) { obj->reset(); }
    int DataLog_size(DataLog* obj) { return obj->data.size(); }
    int DataLog_cols(DataLog* obj) { return obj->cols; }
    double DataLog_next(DataLog* obj) { return obj->next(); }
}