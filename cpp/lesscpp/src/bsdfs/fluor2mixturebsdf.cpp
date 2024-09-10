/*
    Mixture BSDF with fluorescence - a custom plugin

    This file is part of Mitsuba, a physically based rendering system.

    Copyright (c) 2007-2014 by Wenzel Jakob and others.

    Mitsuba is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License Version 3
    as published by the Free Software Foundation.

    Mitsuba is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/texture.h>
#include <mitsuba/core/pmf.h>

MTS_NAMESPACE_BEGIN

/*! \plugin{fluor2mixturebsdf}{Mixture material with fluorescence}
 * \order{16}
 * \parameters{
 *     \parameter{weights}{\String}{A comma-separated list of BSDF weights}
 *     \parameter{\Unnamed}{\BSDF}{Multiple BSDF instances that should be
 *     mixed according to the specified weights}
 * }
 *
 * This plugin implements a ``mixture'' material, which represents
 * linear combinations of multiple BSDF instances. Any surface scattering
 * model in Mitsuba (be it smooth, rough, reflecting, or transmitting) can
 * be mixed with others in this manner to synthesize new models. There
 * is no limit on how many models can be mixed, but their combination
 * weights must be non-negative and sum to a value of one or less to ensure
 * energy balance. When they sum to less than one, the material will
 * absorb a proportional amount of the incident illlumination.
 */

class Fluor2MixtureBSDF : public BSDF {
public:
    Fluor2MixtureBSDF(const Properties &props)
        : BSDF(props) {
        /* Parse the weight parameter */

        std::vector<std::string> weights =
            tokenize(props.getString("weights", ""), " ,;");
        if (weights.size() == 0)
            Log(EError, "No weights were supplied!");
        m_weights.resize(weights.size());

        char *end_ptr = NULL;
        for (size_t i=0; i<weights.size(); ++i) {
            Float weight = (Float) strtod(weights[i].c_str(), &end_ptr);
            if (*end_ptr != '\0')
                SLog(EError, "Could not parse the BSDF weights!");
            if (weight < 0)
                SLog(EError, "Invalid BSDF weight!");
            m_weights[i] = weight;
        }

        // BEGIN Fluorescence

        /* Parse the excitation-fluorescence matrix parameter */
        if (IS_FLUSPECT_PRO) {
            parseEFMatrix(props, "Mb", m_M.m_Mbi);
            parseEFMatrix(props, "Mf", m_M.m_Mfi);
            parseSpectrumTxt(props, "phi", m_phiI);
            m_fqeI = props.getFloat("fqe");//, 0.012
        }
        else {
            parseEFMatrix(props, "Mbi", m_M.m_Mbi);
            parseEFMatrix(props, "Mfi", m_M.m_Mfi);
            parseEFMatrix(props, "Mbii", m_M.m_Mbii);
            parseEFMatrix(props, "Mfii", m_M.m_Mfii);
            parseSpectrumTxt(props, "phiI", m_phiI);
            parseSpectrumTxt(props, "phiII", m_phiII);
            m_fqeI = props.getFloat("fqeI");//, 0.002
            m_fqeII = props.getFloat("fqeII");// , 0.01
        }
        parseSpectrumTxt(props, "kChlrel", m_kChlrel);
        // END Fluorescence
    }

    Fluor2MixtureBSDF(Stream *stream, InstanceManager *manager)
     : BSDF(stream, manager) {
        size_t bsdfCount = stream->readSize();
        m_weights.resize(bsdfCount);
        for (size_t i=0; i<bsdfCount; ++i) {
            m_weights[i] = stream->readFloat();
            BSDF *bsdf = static_cast<BSDF *>(manager->getInstance(stream));
            bsdf->incRef();
            m_bsdfs.push_back(bsdf);
        }
        configure();
    }

    virtual ~Fluor2MixtureBSDF() {
        for (size_t i=0; i<m_bsdfs.size(); ++i)
            m_bsdfs[i]->decRef();
    }

    void serialize(Stream *stream, InstanceManager *manager) const {
        BSDF::serialize(stream, manager);

        stream->writeSize(m_bsdfs.size());
        for (size_t i=0; i<m_bsdfs.size(); ++i) {
            stream->writeFloat(m_weights[i]);
            manager->serialize(stream, m_bsdfs[i]);
        }
    }

    void configure() {
        m_usesRayDifferentials = false;
        size_t componentCount = 0;

        if (m_bsdfs.size() != m_weights.size())
            Log(EError, "BSDF count mismatch: " SIZE_T_FMT " bsdfs, but specified " SIZE_T_FMT " weights",
                m_bsdfs.size(), m_bsdfs.size());

        Float totalWeight = 0;
        for (size_t i=0; i<m_weights.size(); ++i)
            totalWeight += m_weights[i];

        if (totalWeight <= 0)
            Log(EError, "The weights must sum to a value greater than zero!");

        if (m_ensureEnergyConservation && totalWeight > 1) {
            std::ostringstream oss;
            Float scale = 1.0f / totalWeight;
            oss << "The BSDF" << endl << toString() << endl
                << "potentially violates energy conservation, since the weights "
                << "sum to " << totalWeight << ", which is greater than one! "
                << "They will be re-scaled to avoid potential issues. Specify "
                << "the parameter ensureEnergyConservation=false to prevent "
                << "this from happening.";
            Log(EWarn, "%s", oss.str().c_str());
            for (size_t i=0; i<m_weights.size(); ++i)
                m_weights[i] *= scale;
        }

        for (size_t i=0; i<m_bsdfs.size(); ++i)
            componentCount += m_bsdfs[i]->getComponentCount();

        m_pdf = DiscreteDistribution(m_bsdfs.size());
        m_components.reserve(componentCount);
        m_components.clear();
        m_indices.reserve(componentCount);
        m_indices.clear();
        m_offsets.reserve(m_bsdfs.size());
        m_offsets.clear();

        int offset = 0;
        for (size_t i=0; i<m_bsdfs.size(); ++i) {
            const BSDF *bsdf = m_bsdfs[i];
            m_offsets.push_back(offset);

            for (int j=0; j<bsdf->getComponentCount(); ++j) {
                int componentType = bsdf->getType(j);
                m_components.push_back(componentType);
                m_indices.push_back(std::make_pair((int) i, j));
            }

            offset += bsdf->getComponentCount();
            m_usesRayDifferentials |= bsdf->usesRayDifferentials();
            m_pdf.append(m_weights[i]);
        }
        m_pdf.normalize();
        BSDF::configure();
    }

    Spectrum eval(const BSDFSamplingRecord& bRec, EMeasure measure) const {
        Spectrum result(0.0f);

        if (bRec.component == -1) {
            for (size_t i=0; i<m_bsdfs.size(); ++i)
                result += m_bsdfs[i]->eval(bRec, measure) * m_weights[i];
        } else {
            /* Pick out an individual component */
            int idx = m_indices[bRec.component].first;
            BSDFSamplingRecord bRec2(bRec);
            bRec2.component = m_indices[bRec.component].second;
            return m_bsdfs[idx]->eval(bRec2, measure) * m_weights[idx];
        }

        return result;
    }

    Spectrum evalWithEF(const BSDFSamplingRecord& bRec,
        FluorMatrixs ms, FluorMatrix& m, EMeasure measure) const {
        Spectrum result(0.0f);
        FluorMatrix tm;
        if (bRec.component == -1) {
            for (size_t i = 0; i < m_bsdfs.size(); ++i) {
                result += m_bsdfs[i]->evalWithEF(bRec, ms, tm) * m_weights[i];
                if (tm.isFluorMatrixNotZeros()) {
                    if (m_weights[0] == m_weights[1])
                        m.compute_PlusEqual(tm);
                    else
                        m.compute_PlusEqual_M1(tm, m_weights[i]);
                }
            }
        }
        else {
            /* Pick out an individual component */
            int idx = m_indices[bRec.component].first;
            BSDFSamplingRecord bRec2(bRec);
            bRec2.component = m_indices[bRec.component].second;
            result = m_bsdfs[idx]->evalWithEF(bRec, ms, m) * m_weights[idx];
            if (m_weights[0] != m_weights[1])
                m.compute_MultiplyEqual(m_weights[idx]);
        }
        return result;
    }

    Float pdf(const BSDFSamplingRecord &bRec, EMeasure measure) const {
        Float result = 0.0f;

        if (bRec.component == -1) {
            for (size_t i=0; i<m_bsdfs.size(); ++i)
                result += m_bsdfs[i]->pdf(bRec, measure) * m_pdf[i];
        } else {
            /* Pick out an individual component */
            int idx = m_indices[bRec.component].first;
            BSDFSamplingRecord bRec2(bRec);
            bRec2.component = m_indices[bRec.component].second;
            return m_bsdfs[idx]->pdf(bRec2, measure);
        }

        return result;
    }

    Spectrum sample(BSDFSamplingRecord &bRec, const Point2 &_sample) const {
        Point2 sample(_sample);
        if (bRec.component == -1) {
            /* Choose a component based on the normalized weights */
            size_t entry = m_pdf.sampleReuse(sample.x);

            Float pdf;
            Spectrum result = m_bsdfs[entry]->sample(bRec, pdf, sample);
            if (result.isZero()) // sampling failed
                return result;

            result *= m_weights[entry] * pdf;
            pdf *= m_pdf[entry];

            EMeasure measure = BSDF::getMeasure(bRec.sampledType);
            for (size_t i=0; i<m_bsdfs.size(); ++i) {
                if (entry == i)
                    continue;
                pdf += m_bsdfs[i]->pdf(bRec, measure) * m_pdf[i];
                result += m_bsdfs[i]->eval(bRec, measure) * m_weights[i];
            }

            bRec.sampledComponent += m_offsets[entry];
            return result / pdf;
        } else {
            /* Pick out an individual component */
            int requestedComponent = bRec.component;
            int bsdfIndex = m_indices[requestedComponent].first;
            bRec.component = m_indices[requestedComponent].second;
            Spectrum result = m_bsdfs[bsdfIndex]->sample(bRec, sample)
                * m_weights[bsdfIndex];
            bRec.component = bRec.sampledComponent = requestedComponent;
            return result;
        }
    }
    Spectrum sampleWithEF(BSDFSamplingRecord& bRec, const Point2& _sample, 
        FluorMatrixs ms,FluorMatrix& m) const {
        Point2 sample(_sample);
        if (bRec.component == -1) {
            /* Choose a component based on the normalized weights */
            size_t entry = m_pdf.sampleReuse(sample.x);
            Float pdf;
            Spectrum result = m_bsdfs[entry]->sampleWithEF(bRec, pdf, sample, ms, m);
            if (result.isZero()) // sampling failed
                return result;
            Float m_weights_entry_pdf = m_weights[entry] * pdf;
            result *= m_weights_entry_pdf;
            m.compute_MultiplyEqual(m_weights_entry_pdf);
            pdf *= m_pdf[entry];

            EMeasure measure = BSDF::getMeasure(bRec.sampledType);
            FluorMatrix tm;
            for (size_t i = 0; i < m_bsdfs.size(); ++i) {
                if (entry == i)
                    continue;
                pdf += m_bsdfs[i]->pdf(bRec, measure) * m_pdf[i];
                Spectrum m_bsdfs_i_eval_bRec_measure_m_weights_i_ =
                    m_bsdfs[i]->evalWithEF(bRec, ms, tm, measure) * m_weights[i];
                result += m_bsdfs_i_eval_bRec_measure_m_weights_i_;
                if (tm.isFluorMatrixNotZeros()) {
                    if (m_weights[0] == m_weights[1])
                        m.compute_PlusEqual(tm);
                    else
                        m.compute_PlusEqual_M1(tm, m_weights[i]);
                }
            }

            bRec.sampledComponent += m_offsets[entry];
            m.compute_DivideEqual(pdf);
            return result / pdf;
        }
        else {
            /* Pick out an individual component */
            int requestedComponent = bRec.component;
            int bsdfIndex = m_indices[requestedComponent].first;
            bRec.component = m_indices[requestedComponent].second;
            Spectrum result = m_bsdfs[bsdfIndex]->sampleWithEF(bRec, sample, ms, m)
                * m_weights[bsdfIndex];
            if (m_weights[0] != m_weights[1]) {
                m.compute_MultiplyEqual(m_weights[bsdfIndex]);
            }
            bRec.component = bRec.sampledComponent = requestedComponent;
            return result;
        }
    }

    Spectrum sample(BSDFSamplingRecord &bRec, Float &pdf, const Point2 &_sample) const {
        Point2 sample(_sample);
        if (bRec.component == -1) {
            /* Choose a component based on the normalized weights */
            size_t entry = m_pdf.sampleReuse(sample.x);
            Spectrum result = m_bsdfs[entry]->sample(bRec, pdf, sample);
            if (result.isZero()) // sampling failed
                return result;

            result *= m_weights[entry] * pdf;
            pdf *= m_pdf[entry];

            EMeasure measure = BSDF::getMeasure(bRec.sampledType);
            for (size_t i=0; i<m_bsdfs.size(); ++i) {
                if (entry == i)
                    continue;
                pdf += m_bsdfs[i]->pdf(bRec, measure) * m_pdf[i];
                result += m_bsdfs[i]->eval(bRec, measure) * m_weights[i];
            }

            bRec.sampledComponent += m_offsets[entry];
            return result / pdf;
        } else {
            /* Pick out an individual component */
            int requestedComponent = bRec.component;
            int bsdfIndex = m_indices[requestedComponent].first;
            bRec.component = m_indices[requestedComponent].second;
            Spectrum result = m_bsdfs[bsdfIndex]->sample(bRec, pdf, sample)
                * m_weights[bsdfIndex];
            bRec.component = bRec.sampledComponent = requestedComponent;
            return result;
        }
    }

    Spectrum sampleWithEF(BSDFSamplingRecord& bRec, Float& pdf, const Point2& _sample,
        FluorMatrixs ms, FluorMatrix& m) const {
        Point2 sample(_sample);
        if (bRec.component == -1) {
            /* Choose a component based on the normalized weights */
            size_t entry = m_pdf.sampleReuse(sample.x);
            Spectrum result = m_bsdfs[entry]->sampleWithEF(bRec, pdf, sample, ms, m);
            if (result.isZero()) // sampling failed
                return result;
            Float m_weights_entry_pdf = m_weights[entry] * pdf;
            result *= m_weights_entry_pdf;
            m.compute_MultiplyEqual(m_weights_entry_pdf);
            pdf *= m_pdf[entry];

            EMeasure measure = BSDF::getMeasure(bRec.sampledType);
            FluorMatrix tm;
            for (size_t i = 0; i < m_bsdfs.size(); ++i) {
                if (entry == i)
                    continue;
                pdf += m_bsdfs[i]->pdf(bRec, measure) * m_pdf[i];
                Spectrum m_bsdfs_i_eval_bRec_measure_m_weights_i_ =
                    m_bsdfs[i]->evalWithEF(bRec, ms, tm, measure) * m_weights[i];
                result += m_bsdfs_i_eval_bRec_measure_m_weights_i_;
                if (tm.isFluorMatrixNotZeros()) {
                    if (m_weights[0] != m_weights[1]) {
                        m.compute_PlusEqual_M1(tm, m_weights[i]);
                    }
                    else {
                        m.compute_PlusEqual(tm);
                    }
                }
            }

            bRec.sampledComponent += m_offsets[entry];
            m.compute_DivideEqual(pdf);
            return result / pdf;
        }
        else {
            /* Pick out an individual component */
            int requestedComponent = bRec.component;
            int bsdfIndex = m_indices[requestedComponent].first;
            bRec.component = m_indices[requestedComponent].second;
            Spectrum result = m_bsdfs[bsdfIndex]->sampleWithEF(bRec, sample, ms, m)
                * m_weights[bsdfIndex];
            if (m_weights[0] != m_weights[1]) {
                m.compute_MultiplyEqual(m_weights[bsdfIndex]);
            }
            bRec.component = bRec.sampledComponent = requestedComponent;
            return result;
        }
    }

    void addChild(const std::string &name, ConfigurableObject *child) {
        if (child->getClass()->derivesFrom(MTS_CLASS(BSDF))) {
            BSDF *bsdf = static_cast<BSDF *>(child);
            m_bsdfs.push_back(bsdf);
            bsdf->incRef();
        } else {
            BSDF::addChild(name, child);
        }
    }

    Float getRoughness(const Intersection &its, int component) const {
        int bsdfIndex = m_indices[component].first;
        component = m_indices[component].second;
        return m_bsdfs[bsdfIndex]->getRoughness(its, component);
    }

    FluorMatrixs getFluorMatrixs() const {
        return m_M;
    }

    Spectrum getkChlrel() const {
        return m_kChlrel;
    }

    void getphi(Spectrum &phiI, Spectrum& phiII) const {
        if (IS_FLUSPECT_PRO) {
            phiI = m_phiI;
        }
        else {
            phiI = m_phiI;
            phiII = m_phiII;
        }
    }

    void getfqe(Float& fqeI, Float& fqeII) const {
        if (IS_FLUSPECT_PRO) {
            fqeI = m_fqeI;
        }
        else {
            fqeI = m_fqeI;
            fqeII = m_fqeII;
        }
    }

    Spectrum getepsilon(const Intersection& its) const {
        Spectrum R = m_bsdfs[0]->getDiffuseReflectance(its);
        Spectrum T = m_bsdfs[0]->getDiffuseTransmittance(its);
        return Spectrum(1.0f) - (R + T);
    }

    std::string toString() const {
        std::ostringstream oss;
        oss << "Fluor2MixtureBSDF[" << endl
            << "  id = \"" << getID() << "\"," << endl
            << "  weights = {";
        for (size_t i=0; i<m_bsdfs.size(); ++i) {
            oss << " " << m_weights[i];
            if (i + 1 < m_bsdfs.size())
                oss << ",";
        }
        oss << " }," << endl
            << "  bsdfs = {" << endl;
        for (size_t i=0; i<m_bsdfs.size(); ++i)
            oss << "    " << indent(m_bsdfs[i]->toString(), 2) << "," << endl;
        oss << "  }," << endl
            << "]";
        return oss.str();
    }

    Shader *createShader(Renderer *renderer) const;
    
private:

    /* Parse excitation-fluorescence matrix */
    void parseEFMatrix(const Properties& props, const std::string& name, std::vector<Float>& m) {
        std::vector<std::string> s
            = tokenize(props.getString(name, ""), " ,;\n");
        if (s.size() == 0) {
            SLog(EError, "No %s were supplied!", name.c_str());
        }
        if (s.size() != EXCITATION_SAMPLES * FLUOR_SAMPLES) {
            SLog(EError, "Invalid number of %s matrix elements!", name.c_str());
        }
        m.resize(FLUOR_SAMPLES * EXCITATION_SAMPLES);
        char* fend_ptr = NULL;
        for (size_t i = 0; i < s.size(); ++i) {
            Float v = (Float)strtod(s[i].c_str(), &fend_ptr);
            if (*fend_ptr != '\0') {
                SLog(EError, "Could not parse the %s matrix!", name.c_str());
            }
            if (v < 0) {
                SLog(EError, "Invalid %s matrix!", name.c_str());
            }
            m[i] = v;
        }
    }
    void parseSpectrumTxt(const Properties& props, const std::string& name, Spectrum& m) {
        std::vector<std::string> s = tokenize(props.getString(name, ""), " ,;\n");
        if (s.size() == 0) {
            SLog(EError, "No %s were supplied!", name.c_str());
        }
        if (s.size() != SPECTRUM_SAMPLES) {
            SLog(EError, "Invalid number of %s spectrum elements!", name.c_str());
        }
        char* fend_ptr = NULL;
        for (size_t i = 0; i < s.size(); ++i) {
            Float v = (Float)strtod(s[i].c_str(), &fend_ptr);
            if (*fend_ptr != '\0') {
                SLog(EError, "Could not parse the %s spectrum!", name.c_str());
            }
            if (v < 0) {
                SLog(EError, "Invalid %s spectrum!", name.c_str());
            }
            m[i] = v;
        }
    }

private:
    // END Fluorescence

    MTS_DECLARE_CLASS()
private:
    std::vector<Float> m_weights;
    std::vector<std::pair<int, int> > m_indices;
    std::vector<int> m_offsets;
    std::vector<BSDF *> m_bsdfs;
    DiscreteDistribution m_pdf;

    // BEGIN Fluorescence
    FluorMatrixs m_M;
    Spectrum m_kChlrel;
    Spectrum m_phiI;
    Spectrum m_phiII;
    Float m_fqeI;
    Float m_fqeII;
    // END Fluorescence
};


MTS_IMPLEMENT_CLASS_S(Fluor2MixtureBSDF, false, BSDF)
MTS_EXPORT_PLUGIN(Fluor2MixtureBSDF, "Mixture BSDF with fluorescence")

MTS_NAMESPACE_END
